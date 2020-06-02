from strategy import BasicStrategy
import numpy as np
from sklearn.svm import SVC
import joblib


def min_max_scale(data):
    data_min = np.min(data, axis=0)
    data_max = np.max(data, axis=0)
    data_max[data_max - data_min == 0] = 1
    return (data - data_min) / (data_max - data_min)


class Strategy(BasicStrategy):
    def __init__(self, trade_id, socket=None):
        super().__init__(trade_id, socket)
        self.time_steps = 120
        self.input_dims = self.output_dims * (self.time_steps + 1)
        self.length = self.time_steps
        self.replay_buffer = np.zeros((self.length, 3, self.output_dims))
        self.load_model()

    def load_model(self):
        self.model = [joblib.load('train_model/SVM_agent/weights/' + str(i) + '_SVM_model.m') for i in range(self.output_dims)]

    def get_pred(self):
        X_buy = min_max_scale(self.replay_buffer[:, 0])
        X_amount = min_max_scale(self.replay_buffer[:, 2])[-1].reshape((1, -1))
        X_pred = np.concatenate([X_buy, X_amount]).T
        y_pred = np.asarray([m.predict(x.reshape((1, -1))) for m, x in zip(self.model, X_pred)]).ravel()
        return y_pred

    def pred2amount(self, y_pred, y_curr, position):
        y_pred[y_pred > 0.01] = 1
        y_pred[np.logical_and(position > 0, y_pred < -0.01)] = -1
        y_pred[np.logical_and(position == 0, y_pred < -0.01)] = 0
        y_pred[abs(y_pred) != 1] = 0
        return y_pred * self.unit
