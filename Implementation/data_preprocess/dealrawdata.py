## coding: utf-8
'''
This python file is used to train data in CNN model
'''

from __future__ import absolute_import
from __future__ import print_function
import pickle
import cPickle
import numpy as np
import random
import time
import math
import os
from collections import Counter
from imblearn.ensemble import BalanceCascade
from imblearn.over_sampling import ADASYN
from imblearn.over_sampling import SMOTE


np.random.seed(1337)  # for reproducibility

'''
dealrawdata function
-----------------------------
This function is used to cut the dataset, do shuffle and save into pkl file.

# Arguments
    raw_traindataSet_path: String type, the raw data path of train set
    raw_testdataSet_path: String type, the raw data path of test set
    traindataSet_path: String type, the data path to save train set
    testdataSet_path: String type, the data path to save test set
    batch_size: Int type, the mini-batch size
    maxlen: Int type, the max length of data
    vector_dim: Int type, the number of data vector's dim

'''
def dealrawdata(raw_traindataSet_path, raw_testdataSet_path, traindataSet_path, testdataSet_path, batch_size, maxlen, vector_dim):
    print("Loading data...")
    
    for filename in os.listdir(raw_traindataSet_path):
        if not (filename.endswith(".pkl")):
            continue
        print(filename)
        X_train, train_labels, funcs, filenames, testcases = load_data_binary(raw_traindataSet_path + filename, batch_size, maxlen=maxlen, vector_dim=vector_dim)

        f_train = open(traindataSet_path + filename, 'wb')
        pickle.dump([X_train, train_labels, funcs, filenames, testcases], f_train)
        f_train.close()

    for filename in os.listdir(raw_testdataSet_path):
        if not ("api" in filename):
            continue
        print(filename)
        if not (filename.endswith(".pkl")):
            continue
        X_test, test_labels, funcs, filenames, testcases = load_data_binary(raw_testdataSet_path + filename, batch_size, maxlen=maxlen, vector_dim=vector_dim)

        f_test = open(testdataSet_path + filename, 'wb')
        pickle.dump([X_test, test_labels, funcs, filenames, testcases], f_test)
        f_test.close()

def load_data_binary(dataSetpath, batch_size, maxlen=None, vector_dim=40, seed=113):   
    #load data
    f1 = open(dataSetpath, 'rb')
    X, ids, focus, funcs, filenames, test_cases = pickle.load(f1)
    f1.close()
	
    cut_count = 0
    fill_0_count = 0
    no_change_count = 0
    fill_0 = [0]*vector_dim
    totallen = 0
    if maxlen:
        new_X = []
        for x, i, focu, func, file_name, test_case in zip(X, ids, focus, funcs, filenames, test_cases):
            if len(x) <  maxlen:
                x = x + [fill_0] * (maxlen - len(x))
                new_X.append(x)
                fill_0_count += 1

            elif len(x) == maxlen:
                new_X.append(x)
                no_change_count += 1
                    
            else:
                startpoint = int(focu - round(maxlen / 2.0))
                endpoint =  int(startpoint + maxlen)
                if startpoint < 0:
                    startpoint = 0
                    endpoint = maxlen
                if endpoint >= len(x):
                    startpoint = -maxlen
                    endpoint = None
                new_X.append(x[startpoint:endpoint])
                cut_count += 1
            totallen = totallen + len(x)
    X = new_X
    print(totallen)

    return X, ids, funcs, filenames, test_cases



if __name__ == "__main__":
    batchSize = 32
    vectorDim = 40
    maxLen = 500
    raw_traindataSetPath = "./dl_input/cdg_ddg/train/"
    raw_testdataSetPath = "./dl_input/cdg_ddg/test/"
    traindataSetPath = "./dl_input_shuffle/cdg_ddg/train/"
    testdataSetPath = "./dl_input_shuffle/cdg_ddg/test/"
    dealrawdata(raw_traindataSetPath, raw_testdataSetPath, traindataSetPath, testdataSetPath, batchSize, maxLen, vectorDim)
