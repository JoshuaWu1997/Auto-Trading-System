import pymysql
import urllib
import urllib.request
import re
import numpy as np
import time
import pandas as pd
import datetime

host_port = open('setting.txt', 'r')
[host, port] = host_port.readline().split(',')[:2]


def is_trade():
    date = str(datetime.datetime.now().date())
    n_time = datetime.datetime.now()
    m_start = datetime.datetime.strptime(date + '09:30', '%Y-%m-%d%H:%M')
    m_end = datetime.datetime.strptime(date + '11:30', '%Y-%m-%d%H:%M')
    n_start = datetime.datetime.strptime(date + '13:00', '%Y-%m-%d%H:%M')
    n_end = datetime.datetime.strptime(date + '15:00', '%Y-%m-%d%H:%M')
    return (m_start < n_time < m_end) or (n_start < n_time < n_end)


class Crawler:
    def __init__(self):
        self.conn = pymysql.connect(host=host,
                                    port=int(port),
                                    user='root',
                                    password='123456',
                                    database='crawlerdb',
                                    use_unicode=True)
        self.conn._autocommit = False
        cursor = self.conn.cursor()
        cursor.execute('select stockID from selected_stocks')
        self.stock_list = np.ravel(cursor.fetchall())
        cursor.close()
        self.url = "http://hq.sinajs.cn/list="
        for stock in self.stock_list:
            self.url += stock + ","
        print(self.url)
        self.timestamp = datetime.datetime.utcfromtimestamp(0)
        self.tick = None

    def get_info(self):
        if not is_trade():
            return False
        try:
            html = urllib.request.urlopen(self.url).read().decode('gbk')
        except Exception as identifier:
            print(identifier)
            return False
        pattern = re.compile('var hq_str_(.*?)="(.*?)";', re.S)
        ticks = []
        time_stamps = []
        for item in re.finditer(pattern, html):
            tick = [item[0]] + [item[1].split(',')[3]] + item[1].split(',')[6:9]
            time_stamp = datetime.datetime.strptime(item[1].split(',')[30] + ' ' + item[1].split(',')[31],
                                                    "%Y-%m-%d %H:%M:%S")
            if float(tick[2]) == 0:
                tick[2] = tick[3] = tick[1]
            time_stamps.append(time_stamp)
            ticks.append(tick)
        if min(time_stamps) > self.timestamp:
            self.timestamp = max(time_stamps)
            commit_data = [[tick[0], str(self.timestamp)] + tick[1:] for tick in ticks]
            try:
                tick_cursor = self.conn.cursor()
                tick_cursor.executemany('insert into crawl_data values (%s, %s, %s, %s, %s, %s)', commit_data)
                self.conn.commit()
                tick_cursor.close()
            except pymysql.IntegrityError:
                print('IntegrityError')
                return False
            self.tick = ticks
            return True
        else:
            return False

    def get_history(self, n_time):
        try:
            tick_cursor = self.conn.cursor()
            tick_cursor.execute('select id,price,buy,sell,amount from crawl_data where datetime=%s', str(n_time))
            self.tick = [tick for tick in tick_cursor]
            tick_cursor.close()
        except Exception as identifier:
            print(identifier)
            return False
        return True


class CrawlHistory:
    def __init__(self, socket=None):
        self.socket = socket
        self.conn = pymysql.connect(host=host,
                                    port=int(port),
                                    user='root',
                                    password='123456',
                                    database='crawlerdb',
                                    use_unicode=True)
        self.conn._autocommit = False
        cursor = self.conn.cursor()
        cursor.execute('select stockID from selected_stocks')
        self.stock_list = np.ravel(cursor.fetchall())
        cursor.close()

    def get_history(self):
        history_data = pd.DataFrame(index=self.stock_list)
        pattern = re.compile(
            '{day:"(.*?)",open:"(.*?)",high:"(.*?)",low:"(.*?)".*?volume:"(.*?)".*?}', re.S)
        for stock in self.stock_list:
            url = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=' \
                  + stock + '&scale=5&ma=5&datalen=1023'
            while True:
                try:
                    html = urllib.request.urlopen(url).read()
                    html = html.decode('utf-8')
                    items = re.findall(pattern, html)
                    time.sleep(1)
                    print(stock)
                    break
                except TimeoutError:
                    print('retry')
            try:
                tick_cursor = self.conn.cursor()
                for item in items:
                    if stock == 'sh000016':
                        history_data[item[0]] = 0
                    history_data.loc[stock][item[0]] = float(item[1])
                    tick_cursor.execute(
                        'insert ignore into crawl_data (id,datetime,price,buy,sell,amount) ' +
                        'values (%s, %s, %s, %s, %s, %s)', [stock] + list(item))
                self.conn.commit()
                tick_cursor.close()
            except pymysql.IntegrityError:
                print('IntegrityError')
            if self.socket is not None:
                try:
                    self.socket.send((stock + '\n').encode('utf-8'))
                except Exception as identifier:
                    print(identifier)
                    break
        history_data.to_csv('history_data.csv')
