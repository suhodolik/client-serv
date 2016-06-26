# coding: utf-8

import socket
import pickle
import json
import os.path
import threading
from time import time, ctime, sleep

import charm.core.engine.util as utils
from charm.toolbox.pairinggroup import G1, G2, GT, PairingGroup, ZR, pair


class Server:
    def __init__(self, port, count=1):
        scriptpath = os.path.dirname(__file__)
        self.default_server_path = os.path.join(scriptpath, 'outsoursing_files/')
        self.default_server_file = os.path.join(self.default_server_path, 'tarantino.jpg')


        self._groupObj = PairingGroup('SS512')
        self.UK = {}

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        self.sock.bind((host, port))
        self.sock.listen(count)  # количество клиентов
        pass


    def file_send(self, socket):
        print('Thread for client ' + str(socket) + ' started! Waiting for input...')

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

    # Получение ключей UK
    def get_UK_from_AA(self, sock):
        print('GET UK: start...')
        data = sock.recv(16384)
        encdata = self.encode_data(data)
        self.UK = encdata
        print('GET UK: OK')

    def send_UK_to_client(self, sock):
        data_client = sock.recv(1024)
        data_client = pickle.loads(data_client)
        if data_client['action'] == 'GET UK':
            print('Отправка UK на клиент: передача...')
            sock.send(self.encode_data(self.UK))
        else:
            print('Неизвестный запрос от клиента')
        sock.close()
        print('Отправка UK на клиент: завершено')


    def accept_connection(self):
        conn_socket, addr = self.sock.accept()
        print('connected: ', addr)
        return conn_socket

    def disconnect(self, conn):
        conn.close()

    def encode_data(self, data):
        try:
            enc_data = utils.objectToBytes(data, self._groupObj)
        except:
            print('!!!__ERROR__!!!  Ошибка encode_data')
            return {'!!!__ERROR__!!!  Ошибка encode_data'}
        return enc_data

    def decode_data(self, data):
        try:
            enc_data = utils.bytesToObject(data, self._groupObj)
        except:
            print('!!!__ERROR__!!!  Ошибка decode_data')
            return {'!!!__ERROR__!!!  Ошибка decode_data'}
        return enc_data


if __name__ == "__main__":
    cloud_server = Server(port=1404)
    cloud_server_for_client = Server(port=1405)
    print('инициализация сервера')
    while True:
        connect = cloud_server.accept_connection()
        connect_client = cloud_server_for_client.accept_connection()
        # print('connected: ', adr)
        AA_thread = threading.Thread(target=cloud_server.get_UK_from_AA, args=[connect])
        client_thread = threading.Thread(target=cloud_server_for_client.send_UK_to_client, args=[connect_client])
        client_thread.daemon = True
        AA_thread.daemon = True
        AA_thread.start()
        client_thread.start()


        #my_serv.file_send(connect)
