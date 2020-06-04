"""
@File   :DDPG.py
@Author :JohsuaWu1997
@Date   :28/05/2020
"""
import numpy as np
import torch
from strategy import BasicStrategy

cuda = torch.device('cuda')


class ActorNet(torch.nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(ActorNet, self).__init__()
        self.nn = torch.nn.Sequential(
            torch.nn.Linear(input_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, output_dim),
            torch.nn.Softmax(dim=1)
        )

    def forward(self, x):
        out = self.nn(x)
        return out


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
        self.model = ActorNet(self.input_dims, self.node, self.output_dims).to(cuda)
        self.model.load_state_dict(torch.load(r'train_model\DDPG_agent\DDPG_model.pth'))
        self.model.eval()

    def get_pred(self):
        X_buy = min_max_scale(self.replay_buffer[:, 0]).view(1, -1)
        X_amount = min_max_scale(self.replay_buffer[:, 2])[-1].view(1, -1)
        X_pred = torch.cat([X_buy, X_amount], dim=1)
        return self.model(X_pred).cpu().data.numpy().ravel()

    def pred2amount(self, y_pred, y_curr, position):
        y_pred[y_pred < 0] = 0
        y_pred /= sum(y_pred)
        y_pred = np.floor((self.total_asset * y_pred / y_curr - position) / self.unit / 2)
        return y_pred * self.unit
