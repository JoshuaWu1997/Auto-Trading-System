"""
@File   :mysql_dealer.py
@Author :JohsuaWu1997
@Date   :13/07/2020
"""

import pymysql
import numpy as np
import pandas as pd
from utils import is_today, print_transactions

[host, port, username, passwd] = ['127.0.0.1', 3306, 'root', '123456']


class Dealer:
    def __init__(self, trade_id, unit=100):
        self.trade_id = trade_id
        self.user = pymysql.connect(host=host, port=port, user=username, password=passwd, database='userdb',
                                    use_unicode=True)
        self.crawler = pymysql.connect(host=host, port=port, user=username, password=passwd, database='crawlerdb',
                                       use_unicode=True)
        self.user._autocommit = False
        self.crawler._autocommit = False
        self.stock_list = []
        self.get_stock_list()
        self.position = None
        self.get_position()
        self.unit = unit
        self.cash = 0
        self.net_value = 0
        self.tick = None

    def get_test_ticks(self):
        cursor = self.user.cursor()
        cursor.execute('select begin_datetime,end_datetime from trade_list where t_id=%s', self.trade_id)
        [begin, end] = cursor.fetchall()[0]
        cursor = self.crawler.cursor()
        cursor.execute(
            'select datetime from crawl_data where datetime between %s and %s group by datetime order by datetime',
            [begin, end])
        timestamps = [item[0] for item in cursor]
        cursor.close()
        cursor = self.crawler.cursor()
        cursor.execute(
            'select id,price,buy,sell,amount from crawl_data where datetime between %s and %s order by datetime,id',
            [begin, end])
        ticks = [item for item in cursor]
        ticks = [ticks[i * len(self.stock_list):(i + 1) * len(self.stock_list)] for i in range(len(timestamps))]
        cursor.close()
        ticks = dict(zip(timestamps, ticks))
        print('find total ' + str(len(timestamps)) + ' timestamps, test back starts now')
        self.get_position(timestamps[0])
        return timestamps, ticks

    def get_stock_list(self):
        cursor = self.user.cursor()
        cursor.execute('SELECT stock_id FROM trade_stock where t_id=%s', self.trade_id)
        for item in cursor:
            self.stock_list.append(item[0])
        cursor.close()
        if self.stock_list[0].startswith('all'):
            self.stock_list = []
            cursor = self.crawler.cursor()
            cursor.execute('SELECT id FROM crawl_data group by id')
            for item in cursor:
                self.stock_list.append(item[0])
            cursor.close()
        print(self.stock_list)

    def get_position(self, n_time=None):
        """
        total = 'total possession on stock_i'
        today = 'amount of stock_i bought on today (apply to t+1 policy)'
        available = total - today
        deal_price = 'the MOST RECENT deal price'
        :return: DataFrame
                total   today   available   deal_price  curr_price
        stock1  *       *       *           *           *
        stock2  *       *       *           *           *
        ...
        stock_n *       *       *           *           *
        """
        self.position = pd.DataFrame(0, columns=['total', 'today', 'available', 'deal_price', 'curr_price'],
                                     index=self.stock_list).astype(float)
        # get account info
        cursor = self.user.cursor()
        cursor.execute('select valid_cash from trade_list where t_id= %s', self.trade_id)
        self.cash = np.ravel(cursor.fetchall())[0]
        cursor.close()

        # get total position info
        cursor = self.user.cursor()
        cursor.execute('select stock_id,volume from position where t_id= %s', self.trade_id)
        for i in cursor:
            self.position.loc[i[0]]['total'] = float(i[1])
        cursor.close()

        # get today transaction info
        cursor = self.user.cursor()
        cursor.execute('select stock_id,volume,direction,price,transaction_datetime ' +
                       'from trade_detail where t_id= %s', self.trade_id)
        for i in cursor:
            if i[2] == 'buy' and is_today(i[4], n_time):
                self.position.loc[i[0]]['today'] += float(i[1])
                self.position.loc[i[0]]['deal_price'] = float(i[3])
        cursor.close()
        self.position['available'] = self.position['total'] - self.position['today']

        # set total asset info
        self.set_total_asset()

    def set_total_asset(self):
        self.net_value = self.cash + np.sum(self.position['total'] * self.position['curr_price'])
        cursor = self.user.cursor()
        cursor.execute('update trade_list set total_asset=%s,valid_cash=%s where t_id= %s',
                       [str(self.net_value), str(self.cash), self.trade_id])
        cursor.execute('commit')
        cursor.close()
        print('current Net Value:\t', self.net_value)
        print(self.position['total'].values.tolist())

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
            self.position.loc[ids[amount > 0], 'today'] += amount[amount > 0]
            self.position.loc[ids[amount < 0], 'available'] += amount[amount < 0]
            self.position.loc[ids, 'total'] += amount

            cursor = self.user.cursor()
            delete_sql = 'delete from position where t_id= %s and stock_id= %s'
            insert_sql = 'insert into position (volume,t_id,stock_id) values (%s,%s,%s)'
            update_sql = 'update position set volume=%s where t_id= %s and stock_id= %s'
            detail_sql = 'insert into trade_detail values (%s,%s,%s,%s,%s,%s)'

            delete_list = np.logical_and(amount < 0, self.position.loc[ids, 'total'].values == 0)
            insert_list = np.logical_and(amount > 0, self.position.loc[ids, 'total'].values == amount)
            update_list = np.logical_not(np.logical_or(delete_list, insert_list))

            direct_str = np.asarray(['buy' if i > 0 else 'sell' for i in amount])
            insert_update = np.asarray([(str(self.position.loc[ids[i], 'total']), self.trade_id, ids[i]) for i in
                                        range(len(ids))])
            delete = np.asarray([(self.trade_id, ids[i]) for i in range(len(ids))])
            detail = np.asarray(
                [(self.trade_id, ids[i], str(n_time), str(amount[i]), direct_str[i], str(price[i])) for i in
                 range(len(ids))])

            cursor.executemany(delete_sql, delete[delete_list].tolist())
            cursor.executemany(update_sql, insert_update[update_list].tolist())
            cursor.executemany(insert_sql, insert_update[insert_list].tolist())
            cursor.executemany(detail_sql, detail.tolist())
            cursor.execute('commit')
            cursor.close()
            print_transactions(ids, price, amount)

            self.position.loc[s_id, 'curr_price'] = curr[:, 0]
            self.set_total_asset()
