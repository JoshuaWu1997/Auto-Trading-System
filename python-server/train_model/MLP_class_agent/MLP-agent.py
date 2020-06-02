"""
@File   :main.py
@Author :JohsuaWu1997
@Date   :01/05/2020
"""
import pandas as pd
import numpy as np
import torch

cuda = torch.device('cuda')
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
    raw_X = scale(raw_Y)
    raw_X = np.asarray([np.append(raw_X[i - lb:i, :].ravel(), amount[i, :]) for i in range(lb, raw_X.shape[0])])
    raw_Y = raw_Y[lb:, :] - raw_Y[lb - 1:-1, :]
    raw_Y[raw_Y > 0.01] = 1
    raw_Y[raw_Y < -0.01] = -1
    return raw_X, raw_Y


def pre_train(buy, amount, lb, node, epoch):
    print('pre-traininig')
    X, y = get_train(buy, scale(amount), lb)
    model = torch.nn.Sequential(
        torch.nn.Linear(X.shape[1], node),
        torch.nn.ReLU(),
        torch.nn.Linear(node, node),
        torch.nn.ReLU(),
        torch.nn.Linear(node, node),
        torch.nn.ReLU(),
        torch.nn.Linear(node, y.shape[1]),
        torch.nn.Tanh()
    ).to(cuda)

    criterion = torch.nn.MSELoss(reduction='sum')
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
    torch_X_train = torch.tensor(X.tolist(), device=cuda)
    torch_Y_train = torch.tensor(y.tolist(), device=cuda)

    for t in range(epoch):
        y_pred = model(torch_X_train)
        # Zero gradients, perform a backward pass, and update the weights.
        loss = criterion(y_pred, torch_Y_train)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if t % 20 == 19:
            print('epoch:', t, 'loss:', loss.item())
    return model


if __name__ == '__main__':
    lb, node, epoch = 36, 1024, 4000
    buy_train = raw_buy[:START, 1:]
    sell_train = raw_sell[:START, 1:]
    amount_train = raw_amount[:START, 1:]
    model = pre_train(buy_train, amount_train, lb, node, epoch)
    torch.save(model.state_dict(), 'MLP_model.pth')
