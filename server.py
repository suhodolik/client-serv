# coding: utf-8

import socket
import threading

class Server():
    def __init__(self, port=1404, count=1):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        self.sock.bind((host, port))
        self.sock.listen(count)  # количество клиентов
        pass

    def file_send(self, conn):
        print('Thread for client ' + str(conn) + ' started! Waiting for input...')

        # headers = conn.recv(1024)
        # print('headers: %s' % headers)

        file_name = 'tarantino.jpg'
        with open('outsoursing_files/' + file_name, 'rb') as file:
            l = file.read(1024)
            while l:
                conn.send(l)
                l = file.read(1024)

        # headers_2 = conn.recv(1024)
        # print('headers_2: %s' % headers_2)


    def connect(self):
        conn_socket, addr = self.sock.accept()
        print('connected: ', addr)
        return conn_socket, addr

    def disconnect(self, conn):
        conn.close()


if __name__ == "__main__":
    my_serv = Server()
    print('инициализация сервера')
    while True:
        connect, adr = my_serv.connect()
        print('connected: ', adr)
        mythread = threading.Thread(target=my_serv.file_send, args=[connect])
        mythread.daemon = True
        mythread.start()
        #my_serv.file_send(connect)
