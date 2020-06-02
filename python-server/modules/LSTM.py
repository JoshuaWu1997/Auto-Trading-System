from strategy import BasicStrategy
import numpy as np
import tensorflow as tf


def scale(data):
    data_min = np.min(data, axis=0)
    data_max = np.max(data, axis=0)
    data_max[data_max - data_min == 0] = 1
    data = (data - data_min) / (data_max - data_min)
    return data


def LSTMNet(time_steps, input_dims, output_dims, hidden_units):
    Input = tf.keras.Input(shape=(time_steps, input_dims,))
    LSTM = tf.keras.layers.LSTM(hidden_units)(Input)
    Hidden = tf.keras.layers.Dense(hidden_units)(LSTM)
    Output = tf.keras.layers.Dense(output_dims, activation='tanh')(Hidden)
    return tf.keras.Model(inputs=Input, outputs=Output)


class Strategy(BasicStrategy):
    def __init__(self, trade_id, socket=None):
        super().__init__(trade_id, socket)
        self.round = 0
        self.unit = 100
        self.scale = 1000000
        self.node = 512
        self.time_steps = 120
        self.input_dims = self.output_dims * 2
        self.length = self.time_steps
        self.replay_buffer = np.zeros((self.length, 3, self.output_dims))
        self.load_model()

    def load_model(self):
        self.model = LSTMNet(self.time_steps, self.input_dims, self.output_dims, self.node)
        self.model.load_weights(r'train_model\LSTM_class_agent\LSTM_model.h5')

    def get_pred(self):
        X_buy = scale(self.replay_buffer[:, 0])
        X_amount = scale(self.replay_buffer[:, 2])
        X_pred = np.concatenate([X_buy, X_amount], axis=1).reshape((1, self.time_steps, -1))
        return self.model.predict_on_batch(X_pred).numpy().ravel()

    def pred2amount(self, y_pred, y_curr, position):
        y_pred[y_pred > 0.01] = 1
        y_pred[np.logical_and(position > 0, y_pred < -0.01)] = -1
        y_pred[np.logical_and(position == 0, y_pred < -0.01)] = 0
        y_pred[abs(y_pred) != 1] = 0
        return y_pred * self.unit