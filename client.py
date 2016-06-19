# coding: utf-8

import socket
from os.path import expandvars
from time import time, ctime, sleep




def file_get(socket):
    save_time = ctime(time()).replace(' ', '_')
    extension = '.jpg'
    # headers = b'123123'

    # socket.send(headers)
    # path_save = expandvars(u'C:\Users\file_25.jpg').encode('utf-8')
    path_save = 'D:\client_files\\file_' + save_time + '.jpg'
    # name = save_time
    # foo = r'client_files\%s(copy).png' % name
    with open(path_save, 'wb') as f:
    # with open(foo, 'wb') as f:
        print('file opened')
        while True:
            print('receiving data...')
            data = socket.recv(1024)
            # print('data=%s' % data)
            if not data:
                break
            f.write(data)

    print('Successfully get the file')
    socket.send('Successfully get the file')
    # print('connection closed')


if __name__=='__main__':
    TCP_IP = '127.0.0.1'
    TCP_PORT = 1404
    BUFFER_SIZE = 1024

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    s.connect((host, TCP_PORT))
    # s.send(b'HelloWorldEND')
    # upper = s.recv(111)
    # print (upper )
    file_get(socket=s)
    sleep(2)