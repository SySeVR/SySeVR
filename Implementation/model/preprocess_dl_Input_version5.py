## coding:utf-8

import pickle
import numpy as np
import random
from keras.utils import np_utils


np.random.seed(1337)  # for reproducibility


def multi_labels_to_two(label):
    if 1 == label:
        return 1
    else:
        return 0


def mislabels(list_labels, threshold):
    #confuse labels
    label_sum = len(list_labels)
    mispart = int(label_sum*threshold)

    i = 0
    while i < label_sum:
        if i > mispart:
            i += 1
            continue
        if list_labels[i] == 0:
            list_labels[i] = 1
            i += 1
        elif list_labels[i] == 1:
            list_labels[i] = 0
            i += 1

        else:
            print("error")
            exit()
            
    return list_labels


def x_fold_cross_validation_binary(dataset, labels, batch_size, folder=5):
    len_dataset = len(dataset)
    if len(dataset) % folder == 0:
        snippet_width = int(len_dataset/folder)
    else:
        snippet_width = int(len_dataset/folder) + 1 

    list_snippet_dataset = []
    list_snippet_labels = []
    for i in range(0, folder):
        if i != folder-1:
            list_snippet_dataset.append(dataset[i*snippet_width:(i+1)*snippet_width])
            list_snippet_labels.append(labels[i*snippet_width:(i+1)*snippet_width])
        else:
            list_snippet_dataset.append(dataset[i*snippet_width:])
            list_snippet_labels.append(labels[i*snippet_width:])


    list_dataset_all = [[[], [], [], []],[[], [], [], []],[[], [], [], []],[[], [], [], []],[[], [], [], []]]
    for i in range(0, len(list_snippet_dataset)):
        list_train_dataset = []
        list_train_labels = []
        train_dataset = []
        train_labels = []
        test_dataset = []
        test_labels = []

        for j in range(0, len(list_snippet_dataset)):
            if j == i:
                continue
            else:
                list_train_dataset += list_snippet_dataset[j]
                list_train_labels += list_snippet_labels[j]

        train_data_num = len(list_train_dataset)
        train_remain = train_data_num % batch_size

        if train_remain != 0:
            train_dataset = list_train_dataset[:train_data_num-train_remain]
            train_labels = list_train_labels[:train_data_num-train_remain]
        else:
            train_dataset = list_train_dataset
            train_labels = list_train_labels
        
        test_data_num = len(list_snippet_dataset[i])
        test_remain = test_data_num % batch_size

        if test_remain != 0:
            test_dataset = list_snippet_dataset[i][:test_data_num-test_remain]
            test_labels = list_snippet_labels[i][:test_data_num-test_remain]
        else:
            test_dataset = list_snippet_dataset[i]
            test_labels = list_snippet_labels[i]
        list_dataset_all[i][0] = train_dataset
        list_dataset_all[i][1] = train_labels
        list_dataset_all[i][2] = test_dataset
        list_dataset_all[i][3] = test_labels

    return list_dataset_all

def load_data_binary(dataSetpath, batch_size, maxlen=None, vector_dim=40, seed=113):   
    #load data
    f1 = open(dataSetpath, 'rb')
    X, labels, focuspointers = pickle.load(f1)
    f1.close()

    cut_count = 0
    fill_0_count = 0
    no_change_count = 0
    fill_0 = [0]*vector_dim
    if maxlen:
        new_X = []
        new_labels = []
        for x, y, focus in zip(X, labels, focuspointers):
            if len(x) > 1000:
                pass
            if len(x) <  maxlen:
                x = x + [fill_0] * (maxlen - len(x))
                new_X.append(x)
                new_labels.append(y)
                fill_0_count += 1

            elif len(x) == maxlen:
                new_X.append(x)
                new_labels.append(y)
                no_change_count += 1
                    
            else:
                startpoint = int(focus - round(maxlen / 2.0))
                endpoint =  int(startpoint + maxlen)
                if startpoint < 0:
                    startpoint = 0
                    endpoint = maxlen
                if endpoint >= len(x):
                    startpoint = -maxlen
                    endpoint = None
                new_X.append(x[startpoint:endpoint])
                new_labels.append(y)
                cut_count += 1

        X = new_X
        labels = new_labels

    num = len(X)
    remain = num % batch_size

    if remain != 0:
        dataset = X[:num-remain]
        _labels = labels[:num-remain]
    else:
        dataset = X
        _labels = labels

    return dataset, _labels


def process_sequences_shape(sequences, maxLen, vector_dim):
    samples = len(sequences)
    nb_samples = np.zeros((samples, maxLen, vector_dim))

    i = 0
    for sequence in sequences:
        m = 0
        for vectors in sequence:
            n = 0
            for values in vectors:
                nb_samples[i][m][n] += values
                n += 1
            m += 1
        i += 1
    return nb_samples


def generator_of_data(data, labels, batchsize, maxlen, vector_dim):
    iter_num = int(len(data) / batchsize)
    i = 0
    
    while iter_num:
        batchdata = data[i:i + batchsize]
        batched_input = process_sequences_shape(batchdata, maxLen=maxlen, vector_dim=vector_dim)
        batched_labels = labels[i:i + batchsize]
        yield (batched_input, batched_labels)
        i = i + batchsize
        
        iter_num -= 1
        if iter_num == 0:
            iter_num = int(len(data) / batchsize)
            i = 0
