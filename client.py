# coding: utf-8

import socket
import os.path
from time import time, ctime, sleep




def file_get(socket, host, port):
    socket.connect((host, port))
    scriptpath = os.path.dirname(__file__)
    save_time = ctime(time()).replace(' ', '_')
    extension = '.jpg'
    path_client_files = os.path.join(scriptpath, 'client_files/' + save_time + extension)

    file_name = socket.recv(64)
    print(file_name.decode('utf-8'))
    socket.connect((host, port))

    with open(path_client_files + save_time + '.jpg', 'wb') as f:
        print('file created')
        while True:
            print('receiving data...')
            data = socket.recv(1024)
            # print('data=%s' % data)
            if not data:
                break
            f.write(data)

    print('Successfully get the file')
    socket.send(b'Successfully get the file')


def file_send(socket):
    scriptpath = os.path.dirname(__file__)
    save_time = ctime(time()).replace(' ', '_')
    extension = '.jpg'
    path_client_files = os.path.join(scriptpath, 'client_files/tarantino.jpg')

    with open(path_client_files, 'rb') as file:
        l = file.read(1024)
        while l:
            socket.send(l)
            l = file.read(1024)
        socket.close()

if __name__=='__main__':
    TCP_IP = '127.0.0.1'
    TCP_PORT = 1404
    BUFFER_SIZE = 1024

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    # s.connect((host, TCP_PORT))
    # s.send(b'HelloWorldEND')
    # upper = s.recv(111)
    # print (upper )
    file_get(socket=s, host=host, port=TCP_PORT)
    sleep(2)