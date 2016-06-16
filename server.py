# coding: utf-8

import socket


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind(('', 1404))
sock.listen(1)  # количество клиентов

conn, addr = sock.accept()


print 'connected: ', addr

while True:
    data = conn.recv(1024)
    if not data:
        break

    conn.send(data.upper())

conn.close()








