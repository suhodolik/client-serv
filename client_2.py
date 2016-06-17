# coding: utf-8

import socket
from time import time, ctime, sleep




def file_get(socket):
    filepath = 'client_files/%s' % ctime(time()).replace(' ', '_')
    extension = '.jpg'

    with open(filepath + extension, 'wb') as f:
        print('file opened')
        while True:
            print('receiving data...')
            data = s.recv(BUFFER_SIZE)
            # print('data=%s' % data)
            if not data:
                f.close()
                print('file close()')
                break
            # write data to a file
            f.write(data)

    print('Successfully get the file')
    s.close()
    print('connection closed')


if __name__=='__main__':
    TCP_IP = 'localhost'
    TCP_PORT = 9001
    BUFFER_SIZE = 1024

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))

    while True:
        file_get(socket=s)
        sleep(2)