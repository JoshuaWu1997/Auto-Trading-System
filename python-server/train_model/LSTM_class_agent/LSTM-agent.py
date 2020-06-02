import pandas as pd
import numpy as np
import tensorflow as tf

START = 10441
END = 13899

raw_amount = pd.read_csv('../sh000016/i_amount.csv', header=0, index_col=0).values
raw_buy = pd.read_csv('../sh000016/o_buy.csv', header=0, index_col=0).values
raw_sell = pd.read_csv('../sh000016/o_sell.csv', header=0, index_col=0).values


def scale(data):
    data_min = np.min(data, axis=0)
    data_max = np.max(data, axis=0)
    data_max[data_max - data_min == 0] = 1
    return (data - data_min) / (data_max - data_min)


def get_train(raw_Y, amount, lb):
    raw_X = scale(raw_Y)
    raw_X = np.concatenate((raw_X, amount), axis=1)
    raw_X = np.asarray([raw_X[i - lb:i, :] for i in range(lb, raw_X.shape[0])])
    raw_Y = raw_Y[lb:, :] - raw_Y[lb - 1:-1, :]
    raw_Y[raw_Y > 0.01] = 1
    raw_Y[raw_Y < -0.01] = -1
    return raw_X, raw_Y


def attention_3d_block(inputs):
    time_steps = tf.keras.backend.int_shape(inputs)[1]
    a = tf.keras.layers.Permute((2, 1))(inputs)
    a = tf.keras.layers.Dense(time_steps, activation='softmax')(a)
    a_probs = tf.keras.layers.Permute((2, 1))(a)
    output_attention_mul = tf.keras.layers.Multiply()([inputs, a_probs])
    return output_attention_mul


def LSTMNet(time_steps, input_dims, output_dims, hidden_units):
    Input = tf.keras.Input(shape=(time_steps, input_dims,))
    LSTM = tf.keras.layers.LSTM(hidden_units, return_sequences=True)(Input)
    Hidden = tf.keras.layers.LSTM(hidden_units, return_sequences=True)(LSTM)
    Hidden = tf.keras.layers.LSTM(hidden_units, return_sequences=True)(Hidden)
    Hidden = tf.keras.layers.BatchNormalization()(Hidden)
    Hidden = attention_3d_block(Hidden)
    Hidden = tf.keras.layers.Flatten()(Hidden)
    Hidden = tf.keras.layers.Dense(hidden_units)(Hidden)
    Output = tf.keras.layers.Dense(output_dims, activation='tanh')(Hidden)
    return tf.keras.Model(inputs=Input, outputs=Output)


def pre_train(buy, amount, lb, node, epoch):
    X, y = get_train(buy, scale(amount), lb)
    model = LSTMNet(X.shape[1], X.shape[2], y.shape[1], node)
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, batch_size=1024, epochs=epoch, verbose=2)
    return model


if __name__ == '__main__':
    lb, node, epoch = 120, 512, 300
    buy_train = raw_buy[:START, 1:]
    sell_train = raw_sell[:START, 1:]
    amount_train = raw_amount[:START, 1:]
    model = pre_train(buy_train, amount_train, lb, node, epoch)
    model.save('LSTM_model.h5')
