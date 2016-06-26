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

        self._taac = TAAC(self._groupObj)
        self._t = 0
        self.AAs = {}
        self._SK = {}
        self._UK = {}
        self._DK = {}
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
        sock = socket.connect((host, port))
        return sock

    def disconnect(self, socket):
        socket.close()

    # получить PK ключи
    def get_PK_from_AA(self, sock, job):
        data = pickle.dumps(job)
        sock.send(data)
        answ_name = sock.recv(1024)
        answer_name = pickle.loads(answ_name)
        print('GET PK for', answer_name['AA_name'])
        self.AAs[answer_name['AA_name']]['PK'] = self.decode_data(sock.recv(16384))
        print('GET PK: "OK"')

    # получить SK ключи
    def get_SK_from_AA(self, sock, job):
        sock.send(pickle.dumps(job))
        # data = pickle.dumps(self.user_identity)
        # sock.send(data)
        answer = sock.recv(16384)
        print('Answer for key request: %s' % self.decode_data(answer))
        if not '!!!__ERROR__!!!' in self.decode_data(answer):
            self._SK = self.decode_data(answer)

    # получить UK ключи
    def get_UK_from_cloud(self, sock):
        sock.send(pickle.dumps({'action': 'GET UK'}))
        data = sock.recv(16384)
        self._UK = self.decode_data(data)
        print(user_identity["user_name"], user_identity["user_attributes"], 'UK успешно обновлен')

        pass

    # вычислить DK ключи

    def _prepare_DK(self):
        self._DK[self._t] = {}
        for attr in self.user_identity['user_attributes']:
            self._DK[self._t] = self._taac.DKeyCom(self._SK[attr], self._UK[attr])
            if self._DK[self._t][attr] != False:
                print(user_identity["user_name"], user_identity["user_attributes"], ': DK вычислен успешно')




    def decrypt_SYM_KEY(self, enc_key):
        print('User attr:', self.user_identity)
        print('     CT:', enc_key)
        dec_key = self._taac.Decrypt(CT=enc_key, GPP=self._GPP, PK_d={},
                                     DK_gid_x_t=self._DK[self._t], gid=user_identity["user_name"])
        print('     Dec CT:', dec_key)
        return dec_key

    def encrypt_SYM_KEY(self, policy, SYM_KEY=None):
        if not SYM_KEY:
            SYM_KEY = groupObj.random(GT)
        enc_key = self._taac.Encrypt(k=SYM_KEY, t_l=self._t, policy_str=policy, GPP=self.GPP, PK_d=self.AAs)
        return enc_key

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
        except Exception as e:
            print('!!!__ERROR__!!!  Ошибка encode_data', e)
            return {'!!!__ERROR__!!!  Ошибка encode_data'}
        return enc_data

    def decode_data(self, data):
        try:
            enc_data = utils.bytesToObject(data, self._groupObj)
        except Exception as e:
            print('!!!__ERROR__!!!  Ошибка decode_data', e)
            return {'!!!__ERROR__!!!  Ошибка decode_data'}
        return enc_data


if __name__ == '__main__':
    groupObj = PairingGroup('SS512')
    TCP_IP = 'localhost'
    TCP_PORT = 9001
    BUFFER_SIZE = 1024
    user_identity = {"user_name": "user_2",
                     "user_attributes": ['ONE', 'TWO']}

    job_SK = {
        "action": 'GET SK',
        "user_identity": user_identity,
    }

    job_PK = {
        "action": 'GET PK',
        "user_identity": user_identity,
    }
    host = socket.gethostname()
    AA_1_port = 14001
    cloud_port = 1405


    user_1 = Client(groupObj, user_identity)

    # подкдючение к AA и получение секретных ключей
    socket_for_AA = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    user_1.connect(socket=socket_for_AA, host=host, port=AA_1_port)
    user_1.get_SK_from_AA(sock=socket_for_AA, job=job_SK)

    sock_for_cloud = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    user_1.connect(socket=sock_for_cloud, host=host, port=cloud_port)
    sleep(5)
    user_1.get_UK_from_cloud(sock=sock_for_cloud)

    socket_for_AA = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    user_1.connect(socket=socket_for_AA, host=host, port=AA_1_port)
    user_1.get_PK_from_AA(sock=socket_for_AA, job=job_PK)


    # user_1.connect(socket=s, host=host, port=AA_1_port)
    # user_1.get_secret_AA_keys(ssocket=s)



    sleep(2)