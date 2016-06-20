# coding: utf-8

import socket
import os.path
import threading
from time import time, ctime, sleep

class Server():
    def __init__(self, port=1404, count=1):
        scriptpath = os.path.dirname(__file__)
        # path_client_files = os.path.join(scriptpath, save_time + extension)
        self.default_server_path = os.path.join(scriptpath, 'outsoursing_files/')
        self.default_server_file = os.path.join(self.default_server_path, 'tarantino.jpg')
        # self.default_server_file = r'/home/ilsu/my_projects/client_serv/outsuorsing_files/tarantino.jpg'
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        self.sock.bind((host, port))
        self.sock.listen(count)  # количество клиентов
        pass

    def file_send(self, socket):
        print('Thread for client ' + str(socket) + ' started! Waiting for input...')

        # headers = conn.recv(1024)
        # print('headers: %s' % headers)

        socket.send('tarantino.jpg'.encode('utf-8'))
        print('send filename')
        # socket.close()

        # socket = self.connect()

        with open(self.default_server_file, 'rb') as file:
            print('File open')
            l = file.read(1024)
            while l:
                socket.send(l)
                # print('sending data...')
                l = file.read(1024)
            print('sending data: END...')
            socket.close()

    def file_get(self, socket):
        save_time = ctime(time()).replace(' ', '_')
        with open(self.default_server_path + save_time + '.jpg', 'wb') as f:
            print('file created')
            while True:
                print('receiving data...')
                data = socket.recv(1024)
                # print('data=%s' % data)
                if not data:
                    break
                f.write(data)

        print('Successfully get the file')

    def connect(self):
        conn_socket, addr = self.sock.accept()
        print('connected: ', addr)
        return conn_socket

    def disconnect(self, conn):
        conn.close()


if __name__ == "__main__":
    my_serv = Server()
    print('инициализация сервера')
    while True:
        connect = my_serv.connect()
        # print('connected: ', adr)
        mythread = threading.Thread(target=my_serv.file_send, args=[connect])
        mythread.daemon = True
        mythread.start()
        #my_serv.file_send(connect)
