# coding: utf-8

import json
import pickle
import os.path
from time import time, ctime, sleep

import socket
from Crypto.Hash import MD5
import charm.core.engine.util as utils
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.pairinggroup import G1, G2, GT, PairingGroup, ZR, pair

from taac import TAAC

class Client:
    def __init__(self, groupObj, GPP):
        self._groupObj = groupObj
        self._SK = {}
        self._UK = {}
        self._GPP = GPP
        self.user_identity = user_identity
        pass

    def act_to_dict(self, action):
        job = {
            'action': action,
            'user_identity': user_identity
        }
        return job

    def bytes_to_data(self, bytes):
        pass

    def connect(self, socket, host, port):
        socket.connect((host, port))

    def disconnect(self, socket):
        socket.close()

    # SK ключи

    def get_SK_from_AA(self, ssocket):
        data = pickle.dumps(self.user_identity)
        ssocket.send(data)
        answer = ssocket.recv(16384)
        print('Answer for key request: %s' % self.decode_data(answer))



    def get_UK_from_cloud(self, sock):
        sock.send(pickle.dumps({'action': 'GET UK'}))
        data = sock.recv(16384)
        self._UK = self.decode_data(data)
        print('UK успешно обновлен')

        pass

    def DKeyCOM(self):
        pass

    def decrypt_sym_key(self):
        pass

    def encrypt_sym_key(self, sym_key, policy):
        # m = groupObj.random(GT)
        # policy = '((ONE or THREE) and (TWO or FOUR))'
        # enc_m = taac.Encrypt(k=, t=, policy_str=policy, GPP, {'aa1': AAs['aa1']['PK'], 'aa2': AAs['aa2']['PK']})
        pass

    def encrypt_file(self):
        pass

    def decrypt_file(self):
        pass

    def send_file_to_server(self):
        pass

    def get_file_from_server(self):
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


if __name__ == '__main__':
    groupObj = PairingGroup('SS512')
    TCP_IP = 'localhost'
    TCP_PORT = 9001
    BUFFER_SIZE = 1024
    user_identity = {"user_name": "user_2",
                     "user_attributes": ['ONE', 'TWO']}

    task_for_server = {
        "action": "get_SK",
        "user_identity": user_identity
    }

    host = socket.gethostname()
    AA_1_port = 14001
    cloud_port = 1404


    user_1 = Client(groupObj, user_identity)

    # подкдючение к AA и получение секретных ключей
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    user_1.connect(socket=s, host=host, port=AA_1_port)
    user_1.get_SK_from_AA(ssocket=s)

    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    user_1.connect(socket=s2, host=host, port=cloud_port)
    sleep(5)
    user_1.get_UK_from_cloud(sock=s2)
    # user_1.connect(socket=s, host=host, port=AA_1_port)
    # user_1.get_secret_AA_keys(ssocket=s)



    sleep(2)