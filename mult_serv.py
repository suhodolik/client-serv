# coding: utf-8

import socket
from threading import Thread
from time import time, ctime, sleep

TCP_IP = 'localhost'
TCP_PORT = 9001
BUFFER_SIZE = 1024


class ClientThread(Thread):

    def __init__(self, ip, port, sock):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        print(" New thread started for %s:  (date: %s)" % (str(port),ctime(time())))

    def run(self, filepath='outsoursing_files/1.png'):
        self.file_send(filepath)

    def file_send(self, filepath):
        filename = filepath
        f = open(filename, 'rb')
        while True:
            l = f.read(BUFFER_SIZE)
            while (l):
                self.sock.send(l)
                #print('Sent ',repr(l))
                l = f.read(BUFFER_SIZE)
            if not l:
                f.close()
                self.sock.close()
                break


    def file_get(self, path_to_save):
        pass


class servClientThread(Nhread):
    pass



class ServerMethods:

    def __init__(self):
        pass

    def file_send(self):
        pass

    def connect(self):
        pass

    def disconnect(self):
        pass

    def file_get(self):
        pass

    def msg_send(self):
        pass

    def msq_get(self):
        pass


if __name__ == '__main__':
    tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcpsock.bind((TCP_IP, TCP_PORT))
    threads = []

    while True:
        tcpsock.listen(5)
        print("Waiting for incoming connections...")
        (conn, (ip, port)) = tcpsock.accept()
        print('Got connection from ', (ip, port))
        newthread = ClientThread(ip, port, conn)
        newthread.start()
        threads.append(newthread)

    for t in threads:
        t.join()
