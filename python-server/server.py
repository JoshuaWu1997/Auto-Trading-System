import socket
import threading
from crawler import CrawlHistory
import importlib

host_port = open('setting.txt', 'r')


# port = host_port.readline().split(',')[3]


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # host = socket.gethostname()
    port = 12345
    server_socket.bind(('localhost', int(port)))
    server_socket.listen(5)
    print('============ SERVER ADDRESS: ' + str(server_socket.getsockname()) + '============')
    while True:
        client_socket, address = server_socket.accept()
        print('++++++++++++++++++ CLIENT ADDRESS: ' + str(address) + ' ++++++++++++++++++')
        try:
            t = ServerThreading(client_socket)
            t.start()
        except Exception as identifier:
            print('Thread starting failed.')
            print(identifier)


class ServerThreading(threading.Thread):
    def __init__(self, clientsocket, recvsize=2048, encoding='utf-8'):
        threading.Thread.__init__(self)
        self._socket = clientsocket
        self._recvsize = recvsize
        self._encoding = encoding

    def run(self):
        client_socket_name = str(self._socket.getsockname())
        print('----------' + client_socket_name + '  starts' + '----------')
        self._socket.send('start\n'.encode(self._encoding))
        msg = ''
        try:
            while True:
                msg += self._socket.recv(self._recvsize).decode(self._encoding)
                print(msg)
                if msg.strip().endswith('over'):
                    msg = msg[:-4]
                    break
        except Exception as identifier:
            self._socket.send('500\n'.encode(self._encoding))
            print(identifier)
        if not msg == '':
            re = msg.split(',')
            if re[0] == 'get_history':
                get = CrawlHistory(self._socket)
                get.get_history()
            else:
                if re[0].strip().endswith('test'):
                    strategy = importlib.import_module('modules.' + re[0].split('.')[0])
                    broker = strategy.Strategy(re[1], self._socket)
                    broker.test()
                elif re[0].strip().endswith('replay'):
                    replay = importlib.import_module('modules.replay')
                    player = replay.Replay(re[1], self._socket)
                    player.test()
                else:
                    strategy = importlib.import_module('modules.' + re[0])
                    broker = strategy.Strategy(re[1], self._socket)
                    broker.run()
        try:
            self._socket.send('over\n'.encode(self._encoding))
            print('#' + msg + '  over')
            self._socket.close()
            print('++++++++++++++++++ CLIENT ADDRESS: ' + client_socket_name + '  closed' + ' ++++++++++++++++++')
        except Exception as identifier:
            print(identifier)
            print('++++++++++++++++++ CLIENT ADDRESS: ' + client_socket_name + '  closed(fail)' + ' ++++++++++++++++++')

    def __del__(self):
        pass


if __name__ == "__main__":
    main()
