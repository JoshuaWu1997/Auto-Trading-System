import pymysql
import urllib
import urllib.request
import re
import numpy as np
import time
import datetime


def is_trade():
    date = str(datetime.datetime.now().date())
    n_time = datetime.datetime.now()
    m_start = datetime.datetime.strptime(date + '9:30', '%Y-%m-%d%H:%M')
    m_end = datetime.datetime.strptime(date + '11:30', '%Y-%m-%d%H:%M')
    n_start = datetime.datetime.strptime(date + '13:00', '%Y-%m-%d%H:%M')
    n_end = datetime.datetime.strptime(date + '15:00', '%Y-%m-%d%H:%M')
    return (m_start < n_time < m_end) or (n_start < n_time < n_end)


class Crawler:
    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1',
                                    port=3306,
                                    user='root',
                                    password='123456',
                                    database='crawlerdb',
                                    use_unicode=True)
        self.conn._autocommit = False
        cursor = self.conn.cursor()
        cursor.execute('select stockID from selected_stocks')
        self.stock_list = np.ravel(cursor.fetchall())
        cursor.close()
        self.url = 'http://hq.sinajs.cn/list='
        for stock in self.stock_list:
            self.url += stock + ','
        print(self.url)
        self.timestamp = datetime.datetime.utcfromtimestamp(0)
        self.tick = None

    def get_info(self):
        if not is_trade():
            return False
        try:
            html = urllib.request.urlopen(self.url,timeout=1).read().decode('gbk')
        except Exception as identifier:
            print(identifier)
            return False
        pattern = re.compile('var hq_str_(.*?)="(.*?),";', re.S)
        commit_data = []
        max_time_stamp = self.timestamp
        for item in re.finditer(pattern, html):
            tmp = item[2].split(',')
            time_stamp = datetime.datetime.strptime(tmp[30] + ' ' + tmp[31], "%Y-%m-%d %H:%M:%S")
            if time_stamp < self.timestamp:
                return False
            elif time_stamp > max_time_stamp:
                max_time_stamp = time_stamp
            tick = [item[1], tmp[3]] + tmp[6:9]
            if float(tick[2]) == 0 or float(tick[3]) == 0:
                tick[2] = tick[3] = tick[1]
            commit_data.append(tick)
        try:
            self.timestamp = max_time_stamp
            tick_cursor = self.conn.cursor()
            tick_cursor.executemany('insert into crawl_data values (%s, \"' + str(max_time_stamp) + '\", %s, %s, %s, %s)', commit_data)
            self.conn.commit()
            tick_cursor.close()
        except pymysql.IntegrityError:
            print('IntegrityError')
            return False
        return True


if __name__ == '__main__':
    crawl = Crawler()
    while True:
        if crawl.get_info():
            print(crawl.timestamp)
        time.sleep(1)
