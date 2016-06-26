# coding: utf-8

import pickle
import socket
import threading
from Crypto.Hash import MD5
import charm.core.engine.util as utils
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.pairinggroup import G1, G2, GT, PairingGroup, ZR, pair

from taac import TAAC
from server import Server


class AA_server:
    def __init__(self, port, count, groupObj, GPP, attributes):  # groupObj ???
        self._groupObj = groupObj
        self._taac = TAAC(groupObj=groupObj)
        self._time_t = 1
        self._GPP = GPP
        # Инициализация АЦ сервера: принимает глобальные параметры и атрибуты, за которые он отвечает
        # Генерирует PK и MSK, хранение в self._AAs
        self._AAs = self._taac.AuthoritySetup(GPP=self._GPP, U=attributes)
        self.attributes = attributes
        self._users = {}
        self._SK = {}
        self._UK = {}
        self._RL = {'ONE': [], 'TWO': [], 'THREE': [], 'FOUR': []}
        self.cloud_server_port = 1404
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        self.sock.bind((host, port))
        self.sock.listen(count)

    # Вырабатывает секретные ключи для пользователя user_name для каждого атрибута из user_attributes

    def _prepare_user_keys(self, user_name, user_attributes):  # user_name='user_1', user_attributes=['ONE', 'TWO', 'SIX']
        self._users[user_name] = user_attributes
        self._SK[user_name] = {}

        for attr in user_attributes:
            if attr in self.attributes:
                self._SK[user_name][attr] = self._taac.SKeyGen(gid=user_name,
                                                         x=attr,
                                                         ST_x=self._AAs['ST'][attr],
                                                         GPP=self._GPP,
                                                         MSK_fi_x=self._AAs['MSK'][attr])

    def _prepare_UK(self):
        # UK = {}
        for attr in self.attributes:
            self._UK[attr] = self._taac.UKeyGen(0,
                                          attr,
                                          self._AAs['ST'][attr],
                                          self._RL,
                                          self._GPP,
                                          self._AAs['MSK'][attr],
                                          self._AAs['PK']['H'])

    def send_UK_to_cloud(self):
        self._prepare_UK()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((socket.gethostname(), self.cloud_server_port))
        s.send(self.encode_data(self._UK))
        s.close()

    # Отправляет клиенту сгенерированные SK, если они генерируются первый раз
    def send_SK_to_user(self, ssocket):
        data_client = ssocket.recv(1024)
        data_client = pickle.loads(data_client)
        if not data_client['user_name'] in self._users:
            self._prepare_user_keys(data_client['user_name'], data_client['user_attributes'])
            by_SK = self.encode_data(self._SK[data_client['user_name']])
            ssocket.send(by_SK)
        else:
            ssocket.send(b'ERROR')
            # by_SK = self.encode_data(self._SK[data_client['user_name']])
            # ssocket.send(by_SK)
        ssocket.close()



    def send_public_keys(self):
        pass

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


    def connect(self):
        conn_socket, addr = self.sock.accept()
        print('connected: ', addr)
        return conn_socket


if __name__ == "__main__":
    groupObj = PairingGroup('SS512')
    taac_obj_gpp = TAAC(groupObj=groupObj)
    GPP = taac_obj_gpp.GlobalSetup()

    AA_1_port = 14001


    AA_1 = AA_server(port=AA_1_port, count=1, groupObj=groupObj, GPP=GPP, attributes=['ONE', 'TWO'])
    print('инициализация сервера')
    while True:
        connect = AA_1.connect()

        AA_1.send_SK_to_user(connect)
        print('Start UK gen')
        AA_1.send_UK_to_cloud()
"""
        mythread = threading.Thread(target=AA_1.get_client_request, args=[connect])
        mythread.daemon = True
        mythread.start()
"""
    # AA_2 = AA_server(port=14002, count=1, groupObj=groupObj)
