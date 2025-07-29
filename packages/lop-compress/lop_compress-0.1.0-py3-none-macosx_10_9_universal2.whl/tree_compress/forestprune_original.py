import sklearn
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.tree import DecisionTreeRegressor
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn import preprocessing
from sklearn.metrics import mean_squared_error
from sklearn import tree
from sklearn.linear_model import Ridge
from sklearn.ensemble import GradientBoostingRegressor

import veritas
import time
from numba import jit
import itertools
import random
import time
import warnings
import gc
import math

from sklearn.linear_model import lasso_path


def difference_array_list(X,tree_list):
    diff_array_list = []
    for tree1 in tree_list:
        diff_array_list.append(difference_array(X,tree1))
    return np.array(diff_array_list)

def difference_array(X, tree_learner):
    node_indicator = tree_learner.decision_path(X)
    values = tree_learner.tree_.value
    vdiffs = []

    for i in range(0,len(X)):
        node_ids = node_indicator.indices[node_indicator.indptr[i] : node_indicator.indptr[i + 1]]
        instance_values = np.ndarray.flatten(values[node_ids])
        diffs = [j-i for i, j in zip(instance_values[:-1], instance_values[1:])]
        row = np.zeros(tree_learner.max_depth)
        row[:len(diffs)] = diffs
        vdiffs.append(row)

    return np.array(vdiffs)

def prune_at(at, node2value, vars1, learning_rate, coef=None):

    if coef is None:
        coef = np.ones(len(at))

    def prune_tree_(t0, t1, n0, n1, depth, vars1, node2value, c):
        if t0.is_internal(n0) and vars1[depth]:
            s = t0.get_split(n0)
            t1.split(n1, s.feat_id, s.split_value)
            prune_tree_(t0, t1, t0.left(n0), t1.left(n1), depth+1, vars1, node2value, c)
            prune_tree_(t0, t1, t0.right(n0), t1.right(n1), depth+1, vars1, node2value, c)
        else:
            t1.set_leaf_value(n1, 0, node2value[n0] * learning_rate * c)


    at_type = veritas.AddTreeType.REGR_MEAN

    at_pruned = veritas.AddTree(1, at_type)
    at_pruned.set_base_score(0, 0)

    for tree_index, t0 in enumerate(at):
        if vars1[tree_index, 0] == 1.0:
            t1 = at_pruned.add_tree()
            prune_tree_(t0, t1, t0.root(), t1.root(), 0, vars1[tree_index, :],
                        node2value[tree_index], coef[tree_index])

    return at_pruned

@jit(nopython=True)
def evaluate_test_error(difference_array_list,Y,vars_z,learning_rate):
    pred = np.zeros(len(Y))
    for i in range(len(vars_z)):
        pred += np.dot(difference_array_list[i],vars_z[i])*learning_rate
    return np.square(np.subtract(Y, pred)).mean()





from numba import jit
import itertools
import random
@jit(nopython=True)
def precompute_predictions(diff_array_list,temp_vars,learning_rate,cycle_ind):

    precompute_pred = np.zeros(len(diff_array_list[0]))
    for i in range(len(diff_array_list)):
        if i != cycle_ind:
            precompute_pred += np.dot(diff_array_list[i],temp_vars[i])*learning_rate

    return precompute_pred

@jit(nopython=True)
def evaluate_candidates(diff_array_list,temp_vars,learning_rate,cycle_ind,candidates,
                        precompute_pred,Y,alpha,W_array, normalization):
    scores = []
    for candidate in candidates:
        temp_vars[cycle_ind] = candidate
        pred_candidate = np.dot(diff_array_list[cycle_ind],candidate)*learning_rate
        pred = np.add(precompute_pred,pred_candidate)
        err = np.sum((Y-pred)**2)/len(Y) + (alpha/normalization)*np.sum(np.dot(W_array[cycle_ind],candidate))
        scores.append(err)
    return scores

@jit(nopython=True)
def eval_obj(Y,diff_array_list,vars_z,learning_rate,alpha,W_array,normalization):
    pred = np.zeros(len(Y))
    regularization = 0
    for i in range(len(vars_z)):
        pred+= learning_rate*np.dot(diff_array_list[i],vars_z[i])
        regularization += np.sum(np.dot(W_array[i],vars_z[i]))

    bias = np.sum((Y-pred)**2)/len(Y)

    return bias + regularization*alpha/normalization

@jit(nopython=True)
def converge_test(sequence, threshold,tail_length):
    diff = np.diff(sequence)
    if len(diff) < (tail_length+1):
        return False
    else:
        return (np.max(np.abs(diff[-tail_length:])) < threshold)


def solve_weighted(Y,tree_list,diff_array_list,alpha,learning_rate,
                                          W_array,normalization,warm_start= []):
    max_depth = tree_list[0].max_depth
    Y = np.array(Y.values)

    vars_z = np.zeros((len(tree_list),max_depth))
    if len(warm_start) > 0:
        vars_z = np.array(warm_start)

    candidates = np.vstack([np.zeros(max_depth),np.tril(np.ones((max_depth,max_depth)))])

    convergence_scores = np.array([])
    converged = False
    ind_counter = 0
    local_best = 9999
    total_inds = 0
    while converged == False:

        cycle_ind = ind_counter % len(vars_z)

        temp_vars= vars_z.copy()
        precompute_pred = precompute_predictions(diff_array_list,temp_vars,learning_rate,cycle_ind)
        scores = evaluate_candidates(diff_array_list,temp_vars,learning_rate,cycle_ind,
                                     candidates,precompute_pred,Y,alpha,W_array,normalization)

        vars_z[cycle_ind] = candidates[np.argmin(scores)]
        convergence_scores = np.append(convergence_scores,eval_obj(Y,diff_array_list,
                                                                   vars_z,learning_rate,alpha,W_array,normalization))
        converged = converge_test(np.array(convergence_scores),10**-6,3)

        ind_counter = ind_counter + 1
        total_inds = total_inds + 1

        #local search
        if converged == True:
            support_indicies = np.where(~np.all(vars_z == 0, axis=1))[0]
            zero_indicies = np.where(np.all(vars_z == 0, axis=1))[0]

            if convergence_scores[-1] > local_best:
                converged = True

            elif len(support_indicies)> 0:
                local_ind = random.choice(support_indicies)
                vars_z[local_ind] = np.zeros(max_depth)

                if len(zero_indicies) > 0:
                    ind_counter = min(zero_indicies)
                    converged = False
                    local_best = convergence_scores[-1]

                else:
                    converged = True

    return vars_z , total_inds

    # Weight Penalties


def get_node_depths(tree1):
    """
    Get the node depths of the decision tree

    >>> d = DecisionTreeClassifier()
    >>> d.fit([[1,2,3],[4,5,6],[7,8,9]], [1,2,3])
    >>> get_node_depths(d.tree_)
    array([0, 1, 1, 2, 2])
    """
    def get_node_depths_(current_node, current_depth, l, r, depths):
        depths += [current_depth]
        if l[current_node] != -1 and r[current_node] != -1:
            get_node_depths_(l[current_node], current_depth + 1, l, r, depths)
            get_node_depths_(r[current_node], current_depth + 1, l, r, depths)

    depths = []
    get_node_depths_(0, 0, tree1.tree_.children_left, tree1.tree_.children_right, depths) 
    return np.array(depths)


def get_node_count(tree_list,best_vars):
    num_nodes = 0
    depths = np.sum(best_vars,axis = 1)
    for i in range(len(best_vars)):
        tree1 = tree_list[i]
        node_depths = get_node_depths(tree1)
        depth_cutoff = depths[i]
        if depth_cutoff > 0:
            num_nodes = num_nodes + sum(node_depths <= depth_cutoff)
    return num_nodes

def nodes_per_layer(tree_list):
    max_depth = tree_list[0].max_depth
    results = []
    for tree1 in tree_list:
        depths = get_node_depths(tree1)
        values,counts = np.unique(depths,return_counts = True)
        diag = np.zeros(max_depth)
        counts = counts[1:]
        diag[:len(counts)] = counts
        results.append(np.diag(diag))

    return np.array(results)

def total_nodes(tree_list):
    return np.sum(tree1.tree_.node_count for tree1 in tree_list) - len(tree_list)

def prune_polish(difference_array_list,Y,vars_z,learning_rate):
    pred_array = []
    for i in range(len(vars_z)):
        if sum(vars_z[i])>0:
            pred_array.append(np.dot(difference_array_list[i],vars_z[i])*learning_rate)

    if len(pred_array) == 0:
        return np.zeros(len(vars_z))

    pred_array = np.transpose(pred_array)
    lm = Ridge(alpha = 0.01, fit_intercept = False).fit(pred_array,Y)
    coef = lm.coef_
    return coef

@jit(nopython=True)
def evaluate_test_error_polished(difference_array_list,Y,vars_z,coef,learning_rate):
    pred = np.zeros(len(Y))
    j = 0
    for i in range(len(vars_z)):
        if sum(vars_z[i])>0:
            pred += np.dot(difference_array_list[i],vars_z[i])*learning_rate*coef[j]
            j+=1
    return np.square(np.subtract(Y, pred)).mean()

def evaluate(difference_array_list,Y,vars_z,coef,learning_rate):
    pred = np.zeros(len(Y))
    j = 0
    for i in range(len(vars_z)):
        if sum(vars_z[i])>0:
            pred += np.dot(difference_array_list[i],vars_z[i])*learning_rate*coef[j]
            j+=1
    return pred
