import socket
import base64

sock = socket.socket()

host = 'localhost'
port = 1404

sock.connect((host, port))
sock.send('hello, world!')

file = open("D:/", "wb")
while 1:
        file = conn.recv(str)
        buf = str.write(1024)
        str = base64.b64decode(buf)
        if not data:
            break

data = sock.recv(1024)
sock.close()

print data