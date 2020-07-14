"""
@File   :redis_dealer.py
@Author :JohsuaWu1997
@Date   :14/07/2020
"""
from dealer import BasicDealer
import redis
import json
import numpy as np
import pandas as pd

[host, port] = ['192.168.137.153', 6379]


class Dealer(BasicDealer):
    def __init__(self, trade_id, unit=100):
        self.redisPool = redis.ConnectionPool(host=host, port=port, decode_responses=True)
        self.marketRedis = redis.Redis(connection_pool=self.redisPool)
        self.positionRedis = redis.Redis(connection_pool=self.redisPool)
        self.listRedis = redis.Redis(connection_pool=self.redisPool)
        self.detailRedis = redis.Redis(connection_pool=self.redisPool)
        self.stockRedis = redis.Redis(connection_pool=self.redisPool)
        self.trade_list = json.loads(self.listRedis.hget('trade_list', trade_id))
        self.trade_position = self.positionRedis.hget('position', trade_id)
        self.trade_position = dict() if self.trade_position is None else json.loads(self.trade_position)
        super().__init__(trade_id, unit)

    def get_test_ticks(self):
        common = self.begin[:max(
            [i + 1 if self.begin[:i + 1] == self.end[:i + 1] else 0 for i in range(len(self.begin))]
        )]

        ticks = dict()
        market_iter = self.marketRedis.hscan_iter('market', match=common + '*', count=10000)
        for time_step in market_iter:
            if self.begin <= time_step[0] <= self.end:
                tick = json.loads(time_step[1])
                tick = [[index] + [
                    float(tick[index][item]) for item in ['price', 'buy', 'sell', 'amount']
                ] for index in self.stock_list]
                ticks[time_step[0]] = tick
        timestamps = list(ticks.keys())
        timestamps.sort()
        print('find total ' + str(len(timestamps)) + ' timestamps, test back starts now')
        self.get_position(timestamps[0])
        return timestamps, ticks

    def get_stock_list(self):
        self.begin = self.trade_list['begin_datetime']
        self.end = self.trade_list['end_datetime']
        self.stock_list.append(self.trade_list['trade_baseline'])
        self.stock_list.extend(json.loads(self.stockRedis.hget('trade_stock', self.trade_id)))
        if self.stock_list[1].startswith('all'):
            self.stock_list.pop()
            stock_list = list(json.loads(self.marketRedis.hget('market', self.begin)).keys())
            stock_list.remove(self.stock_list[0])
            self.stock_list.extend(stock_list)
        print(self.stock_list)

    def get_position(self, n_time=None):
        self.position = pd.DataFrame(0, columns=['volume', 'curr_price'], index=self.stock_list).astype(float)
        market = json.loads(self.marketRedis.hget('market', self.begin))
        self.cash = float(self.trade_list['valid_cash'])
        for key in self.trade_position.keys():
            self.position.loc[key]['volume'] = self.trade_position[key]
        for key in self.stock_list:
            self.position.loc[key]['curr_price'] = float(market[key]['buy'])
        self.set_total_asset()

    def set_total_asset(self):
        self.net_value = self.cash + np.sum(self.position['volume'] * self.position['curr_price'])
        self.trade_list['total_asset'] = self.net_value
        self.trade_list['valid_cash'] = self.cash
        self.listRedis.hset('trade_list', self.trade_id, json.dumps(self.trade_list))
        print('current Net Value:\t', self.net_value)
        print(self.position['volume'].values.tolist())

    def update_database(self, ids, price, amount, n_time):
        for key in self.stock_list:
            self.trade_position[key] = self.position.loc[key]['volume']
        trade_detail = self.detailRedis.hget('trade_detail', self.trade_id)
        trade_detail = json.loads(trade_detail) if trade_detail is not None else dict()
        append_detail = dict()
        for index, p, volume in zip(ids, price, amount):
            direction = 'buy' if volume > 0 else 'sell'
            append_detail['index'] = dict(zip(['volume', 'direction', 'price'], [abs(volume), direction, p]))
        trade_detail[str(n_time)] = append_detail
        self.detailRedis.hset('trade_detail', self.trade_id, json.dumps(trade_detail))
