"""
@File   :main.py
@Author :JohsuaWu1997
@Date   :01/05/2020
"""
import pandas as pd
import numpy as np
from sklearn.svm import SVC
import joblib

raw_amount = pd.read_csv('../sh000016/i_amount.csv', header=0, index_col=0).values
raw_buy = pd.read_csv('../sh000016/o_buy.csv', header=0, index_col=0).values
raw_sell = pd.read_csv('../sh000016/o_sell.csv', header=0, index_col=0).values

START = 10441
END = 13899


def scale(data):
    data_min = np.min(data, axis=0)
    data_max = np.max(data, axis=0)
    data_max[data_max - data_min == 0] = 1
    data = (data - data_min) / (data_max - data_min)
    return data


def get_train(raw_Y, amount, lb):
    raw_X = [
        np.asarray(
            [
                np.append(raw_Y[i - lb:i, j].ravel(), amount[i, j])
                for i in range(lb, raw_Y.shape[0])
            ]
        ) for j in range(raw_Y.shape[1])
    ]
    raw_Y = raw_Y[lb:, :] - raw_Y[lb - 1:-1, :]
    raw_Y[raw_Y > 0] = 1
    raw_Y[raw_Y < 0] = -1
    return raw_X, raw_Y


def pre_train(buy, amount, lb):
    X, y = get_train(scale(buy), scale(amount), lb)
    model = [SVC(kernel='linear', gamma='scale') for _ in range(len(X))]
    for i in range(len(model)):
        model[i].fit(X[i], y[:, i])
    return model


if __name__ == '__main__':
    lb = 12
    buy_train = raw_buy[:START, 1:]
    sell_train = raw_sell[:START, 1:]
    amount_train = raw_amount[:START, 1:]
    model = pre_train(buy_train, amount_train, lb)
    for i in range(len(model)):
        # model[i].save_to_file(str(i) + '_SVM_model.txt')
        joblib.dump(model[i], str(i) + '_SVM_model.m')
