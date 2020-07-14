"""
@File   :dealer.py
@Author :JohsuaWu1997
@Date   :14/07/2020
"""
import numpy as np
import pandas as pd
from utils import print_transactions


class BasicDealer:
    def __init__(self, trade_id, unit=100):
        self.trade_id = str(trade_id)
        self.stock_list = []
        self.get_stock_list()
        self.position = None
        self.get_position()
        self.unit = unit
        self.cash = 0
        self.net_value = 0
        self.tick = None

    def get_test_ticks(self):
        timestamps, ticks = [], []
        pass
        ticks = dict(zip(timestamps, ticks))
        print('find total ' + str(len(timestamps)) + ' timestamps, test back starts now')
        self.get_position(timestamps[0])
        return timestamps, ticks

    def get_stock_list(self):
        pass
        print(self.stock_list)

    def get_position(self, n_time=None):
        self.position = pd.DataFrame(0, columns=['volume', 'curr_price'], index=self.stock_list).astype(float)
        pass
        self.set_total_asset()

    def set_total_asset(self):
        self.net_value = self.cash + np.sum(self.position['volume'] * self.position['curr_price'])
        pass
        print('current Net Value:\t', self.net_value)
        print(self.position['volume'].values.tolist())

    def update_database(self, ids, amount, price, n_time):
        pass

    def process_order(self, s_id, curr, order, n_time):
        if len(order[0]) > 0:
            ids = np.asarray(order[0], dtype=str)
            amount = np.asarray(order[1])
            price = np.asarray([
                curr[s_id == ids[i], 1] if amount[i] > 0 else curr[s_id == ids[i], 0] for i in range(len(ids))
            ]).ravel()

            transaction_buy = np.sum((amount * price)[amount > 0] * 5e-4)
            transaction_sell = -np.sum((amount * price)[amount < 0] * 1.5e-3)
            '''
            transaction_buy = 0
            transaction_sell = 0
            '''
            cost_buy = np.sum((amount * price)[amount > 0])
            cost_sell = np.sum((amount * price)[amount < 0])
            if self.cash < transaction_buy + transaction_sell + cost_buy:
                ids, price, amount = ids[amount < 0], price[amount < 0], amount[amount < 0]
                while len(ids) > 0 and self.cash < transaction_sell:
                    amount[0] += self.unit
                    ids, price, amount = ids[amount < 0], price[amount < 0], amount[amount < 0]
                    transaction_sell = -np.sum((amount * price) * 1.5e-3)
                cost_sell = np.sum((amount * price)[amount < 0])
                cost = cost_sell + transaction_sell
                transaction_cost = transaction_sell
            else:
                cost = cost_sell + transaction_sell + cost_buy + transaction_buy
                transaction_cost = transaction_sell + transaction_buy
            self.cash -= cost
            print('current Order Cost:\t', transaction_cost)
            if len(ids) == 0:
                return -1
            self.position.loc[ids, 'volume'] += amount

            self.update_database(ids, price, amount, n_time)

            print_transactions(ids, price, amount)
            self.position.loc[s_id, 'curr_price'] = curr[:, 0]
            self.set_total_asset()
