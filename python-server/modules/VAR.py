"""
@File   :VAR.py
@Author :JohsuaWu1997
@Date   :27/05/2020
"""
from strategy import BasicStrategy
import numpy as np
import torch

cuda = torch.device('cuda')


class Lasso(torch.nn.Module):
    def __init__(self, input_size, output_dim):
        super(Lasso, self).__init__()
        self.linear = torch.nn.Linear(input_size, output_dim, bias=False)

    def forward(self, x):
        out = self.linear(x)
        return out


def min_max_scale(data):
    data = torch.tensor(data.tolist(), device=cuda)
    data_min = torch.reshape(torch.min(data, 0).values, (1, -1))
    data_max = torch.reshape(torch.max(data, 0).values, (1, -1))
    data_max[data_max - data_min == 0] = 1
    return data_min, data_max, (data - data_min) / (data_max - data_min)


class Strategy(BasicStrategy):
    def __init__(self, trade_id, socket=None):
        super().__init__(trade_id, socket)
        self.alpha = 0.1
        self.time_steps = 36
        self.input_dims = self.output_dims * (self.time_steps + 1)
        self.length = self.time_steps
        self.replay_buffer = np.zeros((self.length, 3, self.output_dims))
        self.load_model()

    def load_model(self):
        self.model = Lasso(self.input_dims, self.output_dims).to(cuda)
        self.model.load_state_dict(torch.load(r'train_model\VAR_agent\VAR_model.pth'))
        self.model.eval()

    def get_pred(self):
        X_min, X_max, X_buy = min_max_scale(self.replay_buffer[:, 0])
        X_amount = min_max_scale(self.replay_buffer[:, 2])[-1][-1].view(1, -1)
        X_pred = torch.cat([X_buy.view(1, -1), X_amount], dim=1)
        y_pred = self.model(X_pred) * (X_max - X_min) + X_min
        return y_pred.cpu().data.numpy().ravel()

    def pred2amount(self, y_pred, y_curr, position):
        y_pred = np.round(y_pred / 0.01) * 0.01
        allocation = (y_pred - y_curr) / y_curr
        allocation[allocation < 0] = 0
        if np.sum(allocation) > 0:
            allocation /= np.sum(allocation)
        allocation = np.floor(
            allocation * self.total_asset / y_curr / self.unit
        ) * self.unit
        return np.clip(allocation - position, -2 * self.unit, 2 * self.unit)
