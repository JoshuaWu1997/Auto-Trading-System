# Auto-Trading-System
An integrated automated trading system for experiments on real-time/backtest market environments. 

## JAVA frontend GUI

A desktop client application designed using components from AWT, SWING and JFreeChart.
    
    1. PnL & SH50 lines: profit rate lines of the portfolio and the SH50 index.
        
    2. Market info: instant changes of prices of all stocks with highlight colours.
        
    3. Trading history: all transactions of current portfolio.
        
    4. Position: the position of current portfolio.

## Python backend algorithms

The backend is designed to make things easy for algorithms' backtests and real-time tests. The interface entrance is in `server.py` which handles the socket communication with clients. This module should be configured according to specific use once and for all.

The trading algorithms are all inherited from the `BasicStrategy` defined in `strategy.py`. The algorithms can be tested on backtest  by calling `test`, on real-time trading test by calling `run` and on replay one portfolio by simply indicating using `replay` strategy.

To develop a new strategy, one need only to inherit the BasicStrategy and override three methods: `load_model`, `get_pred` and `pred2amount`. `load_model` enables one to load the inference model from files or databases, for example:
```
def LSTMNet(time_steps, input_dims, output_dims, hidden_units):
    Input = tf.keras.Input(shape=(time_steps, input_dims,))
    LSTM = tf.keras.layers.LSTM(hidden_units)(Input)
    Hidden = tf.keras.layers.Dense(hidden_units)(LSTM)
    Output = tf.keras.layers.Dense(output_dims, activation='tanh')(Hidden)
    return tf.keras.Model(inputs=Input, outputs=Output)
    
def load_model(self):
    self.model = LSTMNet(self.time_steps, self.input_dims, self.output_dims, self.node)
    self.model.load_weights(r'train_model\LSTM_class_agent\LSTM_model.h5')
```
The design logic of basic strategy follows the procedure of prediction and allocation. Thus, `get_pred` is the place for next tick prediction, for example:
```
def get_pred(self):
    X_buy = scale(self.replay_buffer[:, 0])
    X_amount = scale(self.replay_buffer[:, 2])
    X_pred = np.concatenate([X_buy, X_amount], axis=1).reshape((1, self.time_steps, -1))
    return self.model.predict_on_batch(X_pred).numpy().ravel()
```
The required size of data storage in memory can vary and in different forms, therefore should be predefined in initial method:
```
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
```
`pred2amount` is to construct a set of transactions according to the current market, current portfolio and predictions:
```
def pred2amount(self, y_pred, y_curr, position):
	y_pred[y_pred > 0.01] = 1
	y_pred[np.logical_and(position > 0, y_pred < -0.01)] = -1
	y_pred[np.logical_and(position == 0, y_pred < -0.01)] = 0
	y_pred[abs(y_pred) != 1] = 0
	return y_pred * self.unit
```

## MySQL databases

An example market can be downloaded from: 

GDrive: https://drive.google.com/file/d/12kxx7ccB3uSeskM8e7mbJXcQnJAs57JB/view?usp=sharing

In addition, the `crawler.py` module is an implementation to crawl SH50 real-time market from Sina Finance. This provides a example about data structures in MySQL databases.
