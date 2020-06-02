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
    return (data - data_min) / (data_max - data_min)


class Lasso(torch.nn.Module):
    def __init__(self, input_size, output_dim):
        super(Lasso, self).__init__()
        self.linear = torch.nn.Linear(input_size, output_dim, bias=False)

    def forward(self, x):
        out = self.linear(x)
        return out


def get_train(raw_Y, amount, lb):
    raw_X = np.asarray([np.append(raw_Y[i - lb:i, :].ravel(), amount[i, :]) for i in range(lb, raw_Y.shape[0])])
    raw_Y = raw_Y[lb:, :]
    return raw_X, raw_Y


def pre_train(buy, amount, lb, epoch, alpha=0.1):
    X, y = get_train(scale(buy), scale(amount), lb)
    model = Lasso(X.shape[1], y.shape[1]).to(cuda)
    criterion = torch.nn.MSELoss(reduction='sum')
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
    torch_X_train = torch.tensor(X.tolist(), device=cuda)
    torch_Y_train = torch.tensor(y.tolist(), device=cuda)

    print('pre-traininig')
    for t in range(epoch):
        y_pred = model(torch_X_train)
        loss = criterion(y_pred, torch_Y_train)
        loss += alpha * torch.norm(model.linear.weight, p=1)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if t % 200 == 199:
            print('epoch:', t, 'loss:', loss.item())
    return model


if __name__ == '__main__':
    lb, alpha, epoch = 12, 0.1, 20000
    buy_train = raw_buy[:START, 1:]
    sell_train = raw_sell[:START, 1:]
    amount_train = raw_amount[:START, 1:]
    model = pre_train(buy_train, amount_train, lb, epoch, alpha)
    torch.save(model.state_dict(), 'VAR_model.pth')
