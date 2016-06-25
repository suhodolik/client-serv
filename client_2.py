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

    def data_to_bytes(self, data):
        pass

    def bytes_to_data(self, bytes):
        pass

    def connect(self, socket, host, port):
        socket.connect((host, port))

    def disconnect(self, socket):
        socket.close()

    # SK ключи

    def request_secret_AA_keys(self, ssocket):
        data = pickle.dumps(self.user_identity)
        ssocket.send(data)
        answer = ssocket.recv(1024)
        print('Answer for key request: %s' % answer)


    def get_secret_AA_keys(self, ssocket):
        ssocket.send(pickle.dumps('Give me my keys'))
        ssocket.send(pickle.dumps(self.user_identity))


    def get_UK_keys(self):
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


if __name__ == '__main__':
    groupObj = PairingGroup('SS512')
    TCP_IP = 'localhost'
    TCP_PORT = 9001
    BUFFER_SIZE = 1024
    user_identity = {"user_name": "user_1",
                     "user_attributes": ['ONE', 'TWO']}

    host = socket.gethostname()
    AA_1_port = 14001


    user_1 = Client(groupObj, user_identity)

    # подкдючение к AA и получение секретных ключей
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, AA_1_port))
    user_1.request_secret_AA_keys(ssocket=s)

    sleep(2)