"""
@File   :mysql_dealer.py
@Author :JohsuaWu1997
@Date   :13/07/2020
"""
from dealer import BasicDealer
import pymysql
import numpy as np
import pandas as pd
from utils import is_today

[host, port, username, passwd] = ['127.0.0.1', 3306, 'root', '123456']


class Dealer(BasicDealer):
    def __init__(self, trade_id, unit=100):
        self.user = pymysql.connect(host=host, port=port, user=username, password=passwd, database='userdb',
                                    use_unicode=True)
        self.crawler = pymysql.connect(host=host, port=port, user=username, password=passwd, database='crawlerdb',
                                       use_unicode=True)
        self.user._autocommit = False
        self.crawler._autocommit = False
        super().__init__(trade_id, unit)

    def get_test_ticks(self):
        cursor = self.user.cursor()
        cursor.execute('select begin_datetime,end_datetime from trade_list where t_id=%s', self.trade_id)
        [begin, end] = cursor.fetchall()[0]
        cursor.close()

        cursor = self.crawler.cursor()
        cursor.execute(
            'select datetime from crawl_data where datetime between %s and %s group by datetime order by datetime',
            [begin, end])
        timestamps = [item[0] for item in cursor]
        cursor.close()

        ticks = dict(zip(timestamps, [[] for _ in range(len(timestamps))]))
        for stock_id in self.stock_list:
            cursor = self.crawler.cursor()
            cursor.execute(
                'select id,price,buy,sell,amount,datetime from crawl_data where datetime between %s and %s and id=%s',
                [begin, end, stock_id]
            )
            for item in cursor:
                ticks[item[-1]].append(item[:-1])
            cursor.close()
        print('find total ' + str(len(timestamps)) + ' timestamps, test back starts now')
        self.get_position(timestamps[0])
        return timestamps, ticks

    def get_stock_list(self):
        cursor = self.user.cursor()
        cursor.execute('select trade_baseline from trade_list where t_id= %s', self.trade_id)
        self.stock_list.append(cursor.fetchall()[0][0])
        cursor.close()

        cursor = self.user.cursor()
        cursor.execute('SELECT stock_id FROM trade_stock where t_id=%s order by stock_id', self.trade_id)
        for item in cursor:
            self.stock_list.append(item[0])
        cursor.close()
        if self.stock_list[1].startswith('all'):
            self.stock_list.pop()
            cursor = self.crawler.cursor()
            cursor.execute('SELECT id FROM crawl_data where id!=%s group by id order by id', [self.stock_list[0]])
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

    def update_database(self, ids, price, amount, n_time):
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
