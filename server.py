# coding: utf-8

import socket


class Server():
    def __init__(self, port=1404, count=1):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', port))
        self.sock.listen(count)  # количество клиентов
        pass

    def file_send(self, conn):
        while True:
            data = conn.recv(1024)
            if not data:
                # break
                print ('finish file transfer!!')
                return
            conn.send(data.upper())

    def connect(self):
        conn_socket, addr = self.sock.accept()
        print ('connected: ', addr)
        return conn_socket, addr

    def disconnect(self, conn):
        conn.close()


if __name__ == "__main__":
    my_serv = Server()
    print (111)
    connect, adr = my_serv.connect()
    print (222)
    my_serv.file_send(connect)









