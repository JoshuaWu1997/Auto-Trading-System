import time

import numpy as np
from dealers.mysql_dealer import Dealer
from crawler import Crawler


class BasicStrategy:
    def __init__(self, trade_id, socket=None):
        self.unit = 100
        self.scale = 1000000
        self.trade_id = str(trade_id)
        self.socket = socket

        self.crawler = Crawler()
        self.dealer = Dealer(self.trade_id, self.unit)

        self.n_time = None
        self.tick = None
        self.order = [[], []]

        self.length = 0
        self.round = 0
        self.output_dims = len(self.dealer.stock_list) - 1
        self.replay_buffer = None
        self.model = None

    def process(self):
        print(self.n_time)
        start_time = time.time()  #
        s_id = np.asarray([tick[0] for tick in self.tick])
        curr = np.asarray([tick[2:5] for tick in self.tick], dtype=float)
        self.dealer.process_order(s_id, curr, self.order, self.n_time)
        self.order = self.get_order(s_id, curr)
        end_time = time.time()  #
        print('<<<<<<<<<< process_tick uses ' + str(end_time - start_time) + 's >>>>>>>>>>')  #

    def send_socket(self, is_send):
        try:
            if is_send:
                self.socket.send((str(self.n_time) + ',sent\n').encode('utf-8'))
            else:
                self.socket.send('pass\n'.encode('utf-8'))
            msg = self.socket.recv(1024).decode('utf-8')
            print(msg)
            if msg.strip().endswith('over'):
                raise Exception('Received over from client socket')
            elif not msg.strip().endswith('received'):
                print(msg.strip())
                time.sleep(10)
        except Exception as identifier:
            print('The client socket closed (Termination).')
            print(identifier)
            return False
        return True

    def run(self):
        while True:
            is_send = False
            start_time = time.time()
            if self.crawler.get_info():
                end_time = time.time()
                self.n_time = self.crawler.timestamp
                self.tick = self.crawler.tick
                print('<<<<<<<<<< get_tick uses ' + str(end_time - start_time) + 's >>>>>>>>>>')
                self.process()
                is_send = True
            if self.socket is not None:
                if not self.send_socket(is_send):
                    break
            time.sleep(1)

    def test(self):
        timestamps, ticks = self.dealer.get_test_ticks()
        for self.n_time in timestamps:
            self.tick = ticks[self.n_time]
            print('<<<<<<<<<< get_tick  >>>>>>>>>>')
            self.process()
            if self.socket is not None:
                if not self.send_socket(True):
                    break

    def load_model(self):
        pass

    def get_pred(self):
        return []

    def pred2amount(self, y_pred, y_curr, position):
        return []

    def get_order(self, s_id, curr):
        print('round: ', self.round)
        ids, amount = [], []
        avail = self.dealer.position.loc[s_id, 'volume'].values[1:].ravel()
        if self.round < self.length - 1:
            print('get_data')
            self.replay_buffer[self.round] = curr[1:].T
        else:
            print('broking')
            self.replay_buffer[-1] = curr[1:].T
            y_pred = self.get_pred()
            amount = self.pred2amount(y_pred, curr[1:, 1].ravel(), avail)
            ids = np.asarray(s_id)[1:]
            ids = ids[amount != 0]
            amount = amount[amount != 0]
            self.replay_buffer[:-1] = self.replay_buffer[1:]
        if self.round == 0:
            self.baseline = curr[0, 0]
            print('baseline:\t', self.scale)
        else:
            print('baseline:\t', curr[0, 0] / self.baseline * self.scale)
        self.round += 1
        return ids, amount


if __name__ == '__main__':
    from modules.SVM import Strategy

    broker = Strategy(18)
    broker.test()
