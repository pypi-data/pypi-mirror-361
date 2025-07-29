from pyexpat import model
import time
import numpy as np
from sklearn import base
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import veritas
import tqdm

from scipy.special import expit as sigmoid
from sklearn.metrics import balanced_accuracy_score, root_mean_squared_error
from functools import partial
import warnings

from xgboost import XGBClassifier, XGBRegressor

#  Based on https://github.com/brianliu12437/ForestPruneAISTATS2023/blob/main/Experiments/Experiment-Boosting.ipynb
# - made to work for binary classification
#   ForestPrune::_objective (equivalent of eval_obj & evaluate_candidates uses binary cross
#   entropy loss instead of squared error
# - made to work for Veritas AddTrees, i.e., without relying on scikit-learns
#   ensemble.estimators_[i][0].tree_.value structure

def get_node_depths(at, tree_index):
    def get_node_depths_(t, nid, depth):
        depths.append(depth)
        if t.is_internal(nid):
            get_node_depths_(t, t.left(nid), depth + 1)
            get_node_depths_(t, t.right(nid), depth + 1)

    t = at[tree_index]
    depths = []
    get_node_depths_(t, t.root(), 0)
    return np.array(depths)
    

# https://stackoverflow.com/questions/44916391/how-to-get-or-see-xgboosts-gradient-statistics-value
def logreg_obj_xgb(pred_raw, label01):
    # XGBOOST
    pred_prob = sigmoid(pred_raw)
    grad = pred_prob - label01
    hess = pred_prob * (1.0 - pred_prob)
    return grad, hess


def logreg_obj_sklearn(pred_raw, label01):
    # scikit-learn
    # https://github.com/scikit-learn/scikit-learn/blob/06f9656e4d0c0d248c44da6cfae2669706682913/sklearn/_loss/_loss.pyx.tp#L754
    # See comment in cgradient_half_binomial.
    #if pred_raw > -37:
    hess = np.exp(-pred_raw)  # used as temporary
    grad = ((1 - label01) - label01 * hess) / (1 + hess)  # gradient
    hess = hess / (1.0 + hess)**2                         # hessian
    #else:
    mask = pred_raw <= -37
    hess[mask] = np.exp(pred_raw[mask])  # = 1. order Taylor in exp(pred_raw)
    grad[mask] = hess[mask] - label01[mask]

    return grad, hess


def log_loss(pred_raw, label01, model_type):
    if model_type == "xgb":
        return logreg_obj_xgb(pred_raw, label01)
    elif model_type == "sklearn":
        return logreg_obj_sklearn(pred_raw, label01)
    else:
        raise RuntimeError()


def l2_loss(pred, y, model_type):
    if model_type in ("sklearn", "xgb"):
        grad = pred - y
        hess = np.ones_like(pred)
        return grad, hess
    else:
        raise RuntimeError()


def get_node2value_map_boosting(at, xtrain, ytrain, task="classification", lambd=1.0, model_type="xgb",
                       learning_rate=None):
    """this is for boosting"""

    if task == "classification":
        gradient_fun = partial(log_loss, model_type=model_type)
    elif task == "regression":
        gradient_fun = partial(l2_loss, model_type=model_type)
    else:
        raise RuntimeError(f"invalid task `{task}`")

    def traverse_(t, n, mask, map, grad, hess):
        if t.is_internal(n):
            s = t.get_split(n)
            split_mask = xtrain[:, s.feat_id] < s.split_value
            traverse_(t, t.left(n), mask & split_mask, map, grad, hess)
            traverse_(t, t.right(n), mask & ~split_mask, map, grad, hess)

        gsum = grad[mask].sum()
        hsum = hess[mask].sum()
        # optimal leaf value XGBoost
        w = -gsum / (hsum + lambd)
        if learning_rate is not None and t.is_leaf(n):
            check = np.isclose(w * learning_rate, t.get_leaf_value(n, 0), rtol=1e-4)
            check |= np.isclose(w * learning_rate, 0.0, atol=1e-4)
            if not check:
                warnings.warn(f"{w=:.16f} != {t.get_leaf_value(n, 0):.16f}")
        map[n] = w

    maps = [{} for _ in range(len(at))]
    base_score = at.get_base_score(0)
    # The original code assumes no base score, but we do have one.
    pred_raw = np.full(xtrain.shape[0], base_score)
    grad, hess = gradient_fun(pred_raw, ytrain)
    everything_mask = np.ones(xtrain.shape[0], dtype=bool)
    for tree_index, t in enumerate(at):
        traverse_(t, t.root(), everything_mask, maps[tree_index], grad, hess)
        pred_raw += t.eval(xtrain).ravel()
        grad, hess = gradient_fun(pred_raw, ytrain)
    return maps


def get_node2value_map_rf(clf, at, task='classification'):
    """ need to pass at too because we need the node ids of the at, not the sklearn tree... """
    def traverse_(n_sk, lefts, rights, values, t, n_at, map):
        if t.is_internal(n_at):
            assert lefts[n_sk] != -1 and rights[n_sk] != -1
            traverse_(lefts[n_sk], lefts, rights, values, t, t.left(n_at), map)
            traverse_(rights[n_sk], lefts, rights, values, t, t.right(n_at), map)
        map[n_at] = values[n_sk]
    
    maps = [{} for _ in range(len(clf.estimators_))]
    for tree_index, (estimator, t) in enumerate(zip(clf.estimators_, at)):
        if task == "classification":
            values = estimator.tree_.value[:, 0, 1].flatten()  # positive class
        elif task == "regression":
            values = estimator.tree_.value.flatten()
        else:
            RuntimeError(f"invalid task `{task}`")
        lefts = estimator.tree_.children_left
        rights = estimator.tree_.children_right
        traverse_(0, lefts, rights, values, t, t.root(), maps[tree_index])
    return maps

def get_node2value_map(clf, at, xtrain, ytrain, task, lambd, model_type,
                          learning_rate):
    if isinstance(clf, (XGBClassifier, XGBRegressor)):
        return get_node2value_map_boosting(at, xtrain, ytrain, task, lambd, model_type, learning_rate)
    elif isinstance(clf, (RandomForestClassifier, RandomForestRegressor)):
        return get_node2value_map_rf(clf, at, task)

def get_leafvalues(at, max_depth, x, node2value):
    def traverse_(tree_index, t, n, mask, wmatrix):
        if t.is_internal(n):
            s = t.get_split(n)
            split_mask = x[:, s.feat_id] < s.split_value
            traverse_(tree_index, t, t.left(n), mask & split_mask, wmatrix)
            traverse_(tree_index, t, t.right(n), mask & ~split_mask, wmatrix)
        wmatrix[mask, t.depth(n)] = node2value[tree_index][n]

    def fill_trailing_zeros_inplace(arr):
        n_rows, n_cols = arr.shape
        for i in range(n_rows):
            row = arr[i]
            # Find the last non-zero index
            for j in reversed(range(n_cols)):
                if not np.isnan(row[j]):
                    last_val = row[j]
                    # Fill from j+1 to end
                    for k in range(j + 1, n_cols):
                        row[k] = last_val
                    break

    all_wmatrices = []
    everything_mask = np.ones(x.shape[0], dtype=bool)
    for tree_index, t in enumerate(at):
        wmatrix = np.full((x.shape[0], max_depth + 1), np.nan, dtype=np.float64)
        traverse_(tree_index, t, t.root(), everything_mask, wmatrix)
        # Fill trailing zeros in each row with the last non-zero value
        fill_trailing_zeros_inplace(wmatrix)
        all_wmatrices.append(wmatrix)
    return np.array(all_wmatrices)


def depth_difference_list(at, max_depth, x, node2value):
    leafvalues = get_leafvalues(at, max_depth, x, node2value)
    # reset leaf values for root nodes to zero
    # because only allowing one value per tree would be the same as changing the base score
    # this is also not implemented in the original version
    leafvalues[:, :, 0] = 0.0
    return np.diff(leafvalues, axis=2)


def prune_at(at, node2value, vars1, learning_rate, task, model_type, base_score, coef):

    def prune_tree_(t0, t1, n0, n1, depth, vars1, node2value, c):
        if t0.is_internal(n0) and vars1[depth]:
            s = t0.get_split(n0)
            t1.split(n1, s.feat_id, s.split_value)
            prune_tree_(t0, t1, t0.left(n0), t1.left(n1), depth+1, vars1, node2value, c)
            prune_tree_(t0, t1, t0.right(n0), t1.right(n1), depth+1, vars1, node2value, c)
        else:
            t1.set_leaf_value(n1, 0, node2value[n0] * learning_rate * c)

    # Define the resulting AddTree type based on task and model_type
    if task == "classification":
        if model_type == "xgb":
            at_type = veritas.AddTreeType.CLF_SOFTMAX
        elif model_type == "sklearn":
            at_type = veritas.AddTreeType.CLF_MEAN
    elif task == "regression":
        if model_type == "xgb":
            at_type = veritas.AddTreeType.REGR
        elif model_type == "sklearn":
            at_type = veritas.AddTreeType.REGR_MEAN
    else:
        raise RuntimeError(f"invalid task `{task}`")

    at_pruned = veritas.AddTree(1, at_type)
    at_pruned.set_base_score(0, base_score)

    for tree_index, t0 in enumerate(at):
        if vars1[tree_index, 0] == 1.0:
            t1 = at_pruned.add_tree()
            prune_tree_(t0, t1, t0.root(), t1.root(), 0, vars1[tree_index, :],
                        node2value[tree_index], coef[tree_index])

    return at_pruned


def nodes_per_layer(at):
    max_depth = at.max_depth()
    results = []
    for tree_index in range(len(at)):
        depths = get_node_depths(at, tree_index)
        values, counts = np.unique(depths,return_counts = True)
        diag = np.zeros(max_depth)
        counts = counts[1:]
        diag[:len(counts)] = counts
        results.append(np.diag(diag))
    return np.array(results)


def converge_test(sequence, threshold, tail_length):
    diff = np.diff(sequence)
    if len(diff) < (tail_length+1):
        return False
    else:
        return (np.max(np.abs(diff[-tail_length:])) < threshold)

def get_params(clf, at):
    if isinstance(clf, XGBClassifier):
        task = "classification"
        model_type = "xgb"
        lambd = 1
        lr = clf.learning_rate
        base_score = at.get_base_score(0)
    elif isinstance(clf, XGBRegressor):
        task = "regression"
        model_type = "xgb"
        lambd = 1
        lr = clf.learning_rate
        base_score = at.get_base_score(0)
    elif isinstance(clf, RandomForestClassifier):
        task = "classification"
        model_type = "sklearn"
        lambd = 1e-5
        lr = 1
        base_score = 0.0
    elif isinstance(clf, RandomForestRegressor):
        task = "regression"
        model_type = "sklearn"
        lambd = 1e-5
        lr = 1
        base_score = at.get_base_score(0)
    return lambd, task, model_type, lr, base_score


class ForestPrune:
    def __init__(self, data, clf,
                 max_mvalid_drop=0.005, seed=124):
        self.d = data
        self.at = veritas.get_addtree(clf)
        self.lambd, self.task, self.model_type, self.learning_rate, self.base_score = get_params(clf, self.at)
        
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.regularization_normalization = self.at.num_nodes()

        self.max_depth = self.at.max_depth()
        
        self.node2value = get_node2value_map(clf, self.at, self.d.xtrain, self.d.ytrain, self.task,
                                                 self.lambd, self.model_type, self.learning_rate)
        self.depthdiff_train = depth_difference_list(self.at, self.max_depth, self.d.xtrain,
                                                     self.node2value)
        self.depthdiff_valid = depth_difference_list(self.at, self.max_depth, self.d.xvalid,
                                                     self.node2value)
        self.depthdiff_test = depth_difference_list(self.at, self.max_depth, self.d.xtest,
                                                    self.node2value)

        # [[ 0 0 .. 0],  # all layers removed
        #  [ 1 0 .. 0],  # only first layer
        #  [ 1 1 .. 0],  # only first and second layer
        #    ...
        #  [ 1 1 .. 1]]  # no layer pruning
        self.candidates = np.vstack([
            np.zeros(self.max_depth),
            np.tril(np.ones((self.max_depth, self.max_depth)))
        ])

        self.W = nodes_per_layer(self.at)
        self.alpha_range = np.flip(np.logspace(-6, 2.5, 100))
        self.debug = False
        self.max_mvalid_drop = max_mvalid_drop

    def _eval(self, depthdiff, vars1=None, skip_tree_index=-1, coef=None, base_score=None):
        """
        Evaluate the ensemble using the depth difference matrix.
        You can the contribution of a tree using `skip_tree_index`.
        You can disable layers of a tree using `vars1`. I reused the name.
        """
        if vars1 is None:
            vars1 = np.ones((len(self.at), self.max_depth))
        if coef is None:
            coef = np.ones(len(self.at))
        if base_score is None:
            base_score = self.base_score
        pred_raw = np.full(depthdiff.shape[1], base_score)
        for tree_index in range(depthdiff.shape[0]):
            if tree_index == skip_tree_index:
                continue
            pred_raw += np.dot(depthdiff[tree_index], vars1[tree_index]) \
                            * self.learning_rate \
                            * coef[tree_index]
        return pred_raw

    def _objective(self, y, pred_raw, vars1, alpha, pruned=False):
        if self.task == "classification":
            # When we have already pruned the trees, objective follows the XGBoost standard.
            if self.model_type == "xgb" or pruned == True:
                probs = sigmoid(pred_raw)
            elif self.model_type == "sklearn":
                probs = pred_raw * 1/max(1, float(np.sum(vars1[:, 0] == 1)))

            probs = np.clip(probs, 1e-10, 1 - 1e-10) # Laplace smoothing
            score = - np.mean(y * np.log(probs) + (1-y) * np.log(1-probs))
        elif self.task == "regression":
            if self.model_type == 'sklearn' and pruned == False:
                pred_raw = pred_raw * 1/max(1, float(np.sum(vars1[:, 0] == 1)))
            score = np.mean(0.5 * (pred_raw - y) ** 2)
        else:
            raise RuntimeError(f"invalid task `{self.task}`")

        regularization = 0
        for tree_index in range(len(self.at)):
            regularization += np.sum(np.dot(self.W[tree_index], vars1[tree_index]))
        regularization *= alpha / self.regularization_normalization
        return score + regularization

    def _metric(self, y, pred_raw, vars1=None, pruned=False):
        if vars1 is None:
            # Used to calculate the metric for the original AddTree
            vars1 = np.ones((len(self.at), self.max_depth))
        if self.task == "classification":
            if self.model_type == "xgb" or pruned == True:
                return 1.0 - balanced_accuracy_score(y, pred_raw > 0.0)
            elif self.model_type == "sklearn":
                pred_raw = pred_raw * 1/max(1, float(np.sum(vars1[:, 0] == 1)))
                return 1.0 - balanced_accuracy_score(y, pred_raw > 0.5)
        elif self.task == "regression":
            if self.model_type == 'sklearn' and pruned == False:
                pred_raw = pred_raw * 1/max(1, float(np.sum(vars1[:, 0] == 1)))
            return root_mean_squared_error(y, pred_raw)
        else:
            raise RuntimeError(f"invalid task `{self.task}`")

    def _eval_candidates(self, precomputed_pred_raw, vars1, tree_index, alpha):
        """ Always based on training data! """
        scores = []
        vars1_copy = vars1.copy()
        for c in self.candidates:
            vars1_copy[tree_index, :] = c
            tree_pred_raw = np.dot(self.depthdiff_train[tree_index], c) \
                            * self.learning_rate
            pred_raw = precomputed_pred_raw + tree_pred_raw

            if self.debug:
                assert np.all(np.isclose(self._eval(self.depthdiff_train, vars1_copy), pred_raw))

            score = self._objective(self.d.ytrain, pred_raw, vars1_copy, alpha)
            scores.append(score)
        return scores

    def _solve_weighted(self, alpha):
        depthdiff = self.depthdiff_train
        vars1 = np.zeros((len(self.at), self.max_depth))
        convergence_scores = []
        ind_counter = 0
        local_best = 1e10
        
        for total_inds in range(10_000):
            tree_index = ind_counter % len(vars1)
            # Calculate without selected tree variable
            precomputed_pred_raw = self._eval(depthdiff, vars1, skip_tree_index=tree_index)
            # Vary selected tree variable
            scores = self._eval_candidates(precomputed_pred_raw, vars1, tree_index, alpha, verbose=(total_inds ==100))
            # Select best variable
            best = np.argmin(scores)
            vars1[tree_index] = self.candidates[best]
            convergence_scores.append(scores[best])
            ind_counter += 1

            # Local search
            # Check if the biggest difference in the last 3 iterations is smaller than threshold
            if converge_test(convergence_scores, 1e-6, 3):
                # this currently leads to inf loops for small ensembles
                if len(vars1) < 10:
                    break

                support_indicies = np.where(~np.all(vars1 == 0, axis=1))[0]
                zero_indicies = np.where(np.all(vars1 == 0, axis=1))[0]
                
                if convergence_scores[-1] > local_best:
                    break
                elif len(support_indicies) > 0:
                    local_ind = self.rng.choice(support_indicies)
                    # This sets a random previously enabled member back to 0 again
                    vars1[local_ind] = 0.0
                    #print(f" -> set {local_ind} to zero")
                    if len(zero_indicies) > 0:
                        ind_counter = min(zero_indicies)
                        local_best = convergence_scores[-1]
                    else:
                        break
                elif len(support_indicies) == 0 and total_inds > len(self.at):
                    # we've tried all trees and everything is still just 0 (high alpha)
                    break

        return vars1, total_inds

    def _polish(self, vars1):
        tree_indices = vars1.sum(axis=1).nonzero()[0]
        num_trees = len(tree_indices)

        if num_trees == 0:
            return np.ones(vars1.shape[0]), self.base_score

        pred_per_member = np.zeros((self.d.xtrain.shape[0], num_trees))
        for i, tree_index in enumerate(tree_indices):
            pred = np.dot(self.depthdiff_train[tree_index], vars1[tree_index]) * self.learning_rate
            pred_per_member[:, i] = pred

        if self.task == "classification":
            from sklearn.linear_model import LogisticRegression
            lr = LogisticRegression(fit_intercept=True, n_jobs=1)
            lr.fit(pred_per_member, self.d.ytrain)
            coef = np.zeros(vars1.shape[0])
            coef[tree_indices] = lr.coef_[0]
            return coef, lr.intercept_[0]

        elif self.task == "regression":
            from sklearn.linear_model import Ridge
            # copied from https://github.com/brianliu12437/ForestPruneAISTATS2023/blob/main/Code/ForestPrune.py
            lr = Ridge(alpha=0.01, fit_intercept=False)
            lr.fit(pred_per_member, self.d.ytrain)
            coef = np.zeros(vars1.shape[0])
            coef[tree_indices] = lr.coef_
            intercept = 0.0
            return coef, intercept
            
        else:
            raise RuntimeError(f"invalid task `{self.task}`")

    def prune(self, timeout):
        timer = time.time()
        mvalid = self._metric(self.d.yvalid, self._eval(self.depthdiff_valid))
        nlvs = self.at.num_leafs()

        #     |  0.6067 |  0.5000 |    +inf×

        print(f"score tr | metric val | compr.rat (ref metric val: {mvalid:.4f})")

        prune_results = []
        pbar = tqdm.tqdm(self.alpha_range)
        for alpha in pbar:
            if time.time() - timer > timeout:
                break
            vars1, iters = self._solve_weighted(alpha)
            pred_raw = self._eval(self.depthdiff_train, vars1)
            score = self._objective(self.d.ytrain, pred_raw, vars1, alpha)
            metric = self._metric(self.d.ytrain, pred_raw, vars1)


            coef, intercept = self._polish(vars1)
            pred_raw_polish = self._eval(self.depthdiff_train, vars1, coef=coef,
                                         base_score=intercept)
            score_polish = self._objective(self.d.ytrain, pred_raw_polish, vars1, alpha, pruned=True)
            metric_polish = self._metric(self.d.ytrain, pred_raw_polish, vars1, pruned=True)

            pred_raw_polish = self._eval(self.depthdiff_valid, vars1, coef=coef,
                                         base_score=intercept)
            score_polish = self._objective(self.d.yvalid, pred_raw_polish, vars1, alpha, pruned=True)
            metric_polish = self._metric(self.d.yvalid, pred_raw_polish, vars1, pruned=True)

            lr = max(1, float(np.sum(vars1[:, 0] == 1))) if self.at.get_type() == veritas.AddTreeType.REGR_MEAN else self.learning_rate

            at_pruned = prune_at(self.at, self.node2value, vars1, lr,
                                 base_score=intercept, coef=coef, task=self.task, model_type=self.model_type)

            nlvs_pr = at_pruned.num_leafs()
            compr_rat = f"{nlvs / nlvs_pr:.1f}×" if nlvs_pr > 0 else "+inf"
            pbar.set_description(f"{score:8.4f} |{metric_polish:11.4f} |{compr_rat:>8s}")

            if self.debug:
                metric_check = self._metric(self.d.yvalid, at_pruned.eval(self.d.xvalid)[:, 0], vars1)
                check = np.isclose(metric_check, metric_polish, rtol=1e-3)
                if not check:
                    print("DEBUG METRIC CHECK VIOLATION")
                    print(at_pruned.eval(self.d.xvalid)[:, 0])
                    print(pred_raw_polish)
                assert check, f"{metric_check} != {metric_polish}"
            
            prune_results.append([alpha, at_pruned, score_polish, metric_polish])

        candidates = []
        for i, (alpha, at, score, metric) in enumerate(prune_results):
            nlvs_pr = at.num_leafs()
            compr_rat = f"{nlvs / nlvs_pr:.1f}×" if nlvs_pr > 0 else "+inf"
            if self.task == "classification":
                if metric < mvalid + self.max_mvalid_drop:  # balanced error
                    candidates.append(i)
            elif self.task == "regression":
                if metric < mvalid * (1.0 + self.max_mvalid_drop):  # relative for 
                    candidates.append(i)
            else:
                raise RuntimeError(f"invalid task `{self.task}`")

        if len(candidates) > 0:
            k = np.argmin([prune_results[i][1].num_leafs() for i in candidates])
            winner = candidates[k]
        else:
            return self.at # If pruning doesn't lead to a better model, return the original

        return prune_results[winner][1]  # pruned addtree