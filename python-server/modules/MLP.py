"""
@File   :MLP.py
@Author :JohsuaWu1997
@Date   :27/05/2020
"""
from strategy import BasicStrategy
import numpy as np
import torch

cuda = torch.device('cuda')


def min_max_scale(data):
    data = torch.tensor(data.tolist(), device=cuda)
    data_min = torch.reshape(torch.min(data, 0).values, (1, -1))
    data_max = torch.reshape(torch.max(data, 0).values, (1, -1))
    data_max[data_max - data_min == 0] = 1
    return (data - data_min) / (data_max - data_min)


class Strategy(BasicStrategy):
    def __init__(self, trade_id, socket=None):
        super().__init__(trade_id, socket)
        self.round = 0
        self.unit = 100
        self.scale = 1000000
        self.node = 2048
        self.time_steps = 36
        self.input_dims = self.output_dims * (self.time_steps + 1)
        self.length = self.time_steps
        self.replay_buffer = np.zeros((self.length, 3, self.output_dims))
        self.load_model()

    def load_model(self):
        self.model = torch.nn.Sequential(
            torch.nn.Linear(self.input_dims, self.node),
            torch.nn.ReLU(),
            torch.nn.Linear(self.node, self.node),
            torch.nn.ReLU(),
            torch.nn.Linear(self.node, self.node),
            torch.nn.ReLU(),
            torch.nn.Linear(self.node, self.output_dims),
            torch.nn.Tanh()
        ).to(cuda)
        self.model.load_state_dict(torch.load(r'train_model\MLP_class_agent\MLP_model.pth'))
        self.model.eval()

    def get_pred(self):
        X_buy = min_max_scale(self.replay_buffer[:, 0]).view(1, -1)
        X_amount = min_max_scale(self.replay_buffer[:, 2])[-1].view(1, -1)
        X_pred = torch.cat([X_buy, X_amount], dim=1)
        return self.model(X_pred).cpu().data.numpy().ravel()

    def pred2amount(self, y_pred, y_curr, position):
        y_pred[y_pred > 0.01] = 1
        y_pred[np.logical_and(position > 0, y_pred < -0.01)] = -1
        y_pred[np.logical_and(position == 0, y_pred < -0.01)] = 0
        y_pred[abs(y_pred) != 1] = 0
        return y_pred * self.unit
