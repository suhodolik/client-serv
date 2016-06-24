# coding: utf-8

import socket
import json
import os.path
from time import time, ctime, sleep
import charm.core.engine.util as utils

class Client:
    def __init__(self, groupObj, GPP):
        self._groupObj = groupObj
        self._SK = {}
        self._UK = {}
        self._GPP = GPP
        pass

    def data_to_bytes(self, data):
        pass

    def bytes_to_data(self, bytes):
        pass

    def connect(self, socket, host, port):
        socket.connect((host, port))

    def disconnect(self, socket):
        socket.close()

    def request_secret_AA_keys(self, socket):
        a3 = socket.send('Give me keys')
        print('Message to server: ', a3)

    def get_secret_AA_keys(self, socket):
        keys = socket.recv(1024)
        utils.bytesToObject(keys, group=self._groupObj)
        return keys

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


class TAAC():
    def __init__(self, groupObj):
        #Объявление глобальых переменных
        global group, util
        group = groupObj
        util = SecretUtil(groupObj)

    def GlobalSetup(self):
        #g генератор группы G
        g = group.random(G1)
        #Хэш-функция отображающая глобальный идентификатор пользователя в элемент группы G
        H = lambda x: group.hash(x, G1)
        #GPP - публикуемые глобальные открытые параметры
        return {'g': g, 'H': H}
    #Функция регисрирующая АЦ
    #U - набор атрибутов для данного АЦ
    #GPP возвращается функцией GlobalSetup
    #Возвращает набор PK и MSK ключей для каждого атрибута для даноого АЦ
    #То есть для каждого атрибута свой PK и MSK
    def AuthoritySetup(self, GPP, U):
        PK, MSK, ST, T, h, R, alpha, betta, ctr, List = {}, {}, {}, {}, {}, {}, {}, {}, {}, {}
        #Хэш-функция отображающая пару () в элемент группы G
        H = lambda a, b: group.hash((a, b), G1)
        #Для каждого атрибута из U строится дерево и генерируются экспоненты alpha, betta
        #Для каждого узла построенного дерева генерируются случайные числа Rvx
        for x in U:
            #Генерация экспонент
            alpha[x], betta[x] = group.random(ZR), group.random(ZR)
            #Задание высоты дерева
            h[x] = 3

            ctr[x] = 0
            List[x] = []

            #Дерево задается в виде пронумерованных узлов
            #Начало построения самого дерева: родительский узел дерева
            T[x] = {1: ''}
            #Rvx для родительского узла
            R[x] = {1: group.random(G1)}
            #Для каждого уровня добавляем по 2 узла: правый, левый дочерние узлы
            #хх - родительские узлы, ххх - дочерние узлы для хх
            for xx in range(1, h[x] + 2):
                for xxx in range(1, 2 ** xx):
                    T[x][xxx] = ''
                    #Генерация случайного числа Rvx для узла xxx
                    R[x][xxx] = group.random(G1)
            #Запись состояния атрибута x
            ST[x] = {'x': x, 'h': h[x], 'ctr': ctr[x], 'list': List[x]}
            #Запись PK для атрибута x
            PK[x] = {'e(g,g)^alpha': pair(GPP['g'], GPP['g']) ** alpha[x], 'g^betta': GPP['g'] ** betta[x]}
            #Запись MSK для атрибута x
            MSK[x] = {'alpha': alpha[x], 'betta': betta[x], 'Rx': R[x]}
        #Добавляем к PK хэш-функцию АЦ
        PK['H'] = H
        return {'PK': PK, 'MSK': MSK, 'ST': ST}

    #Функция генерации секретного ключа для атрибута x
    #Возвращает SK для x и новое состояние атрибута x
    #На вход: ST_x, MSK_fi_x - состояние атрибута и мастер-ключ атрибута х соотвествующего АЦ
    def SKeyGen(self, gid, x, ST_x, GPP, MSK_fi_x):

        SK_x = {'K_gid_x': {}}
        u_x_gid = 2 ** ST_x['h'] + ST_x['ctr']
        ST_x['list'].append((gid, u_x_gid))
        ST_x['ctr'] += 1

        #Нахождение пути от прородительского узла к узлу u_x_gid
        path = [u_x_gid]
        while u_x_gid != 1:
            u_x_gid = int(u_x_gid/2)
            path.append(u_x_gid)
        #В итоге path - путь к узлу u_x_gid
        #Для каждого узла состовляющего путь вычисляется часть SK
        for v_x in path:
            SK_x['K_gid_x'][v_x] = GPP['g'] ** MSK_fi_x['alpha'] * GPP['H'](gid) ** MSK_fi_x['betta'] * MSK_fi_x['Rx'][v_x]
        return {'SK': SK_x, 'ST_x': ST_x}

    #Функция обновления узлов
    #Выводит список узлов покрывающих пользователей имеющих право на атрибут x и исключающая остальных пользователей
    #Эту функцию я еще переаботаю, что бы было без флагов
    def KUNodes(self, ST_x, RL_x_t):
        X_r, X_e, N_x_t = [], [], []
        #самый левый пустой узел
        u_e = 2 ** ST_x['h'] + ST_x['ctr'] + 1
        X_e = [u_e]
        while u_e != 1:
            u_e = int(u_e/2)
            X_e.append(u_e)
        X_r = [1]
        for u_r in RL_x_t:
            a = 0
            for x in X_r:
                if u_r == x:
                    a = 1
            if a == 0:
                X_r.append(u_r)
            while u_r != 1:
                a = 0
                u_r = int(u_r / 2)
                for x in X_r:
                    if u_r == x:
                        a = 1
                if a == 0:
                    X_r.append(u_r)

        for r in X_r:
            for el in X_r:
                for el2 in X_e:
                    if el == el2:
                        X_r.remove(el)
        for v_e in X_e:
            if v_e < 2 ** ST_x['h']:
                v_l_c = 2 * v_e
                a = 0
                for el in (X_e + X_r):
                    if el == v_l_c:
                        a = 1
                if a == 0:
                    N_x_t.append(v_l_c)

        for v_r in X_r:
            if v_r < 2 ** ST_x['h']:
                v_l_c = 2 * v_r
                a = 0
                for el in X_r:
                    if el == v_l_c:
                        a = 1
                if a == 0:
                    N_x_t.append(v_l_c)
                v_r_c = 2 * v_r + 1
                a = 0
                for el in X_r:
                    if el == v_r_c:
                        a = 1
                if a == 0:
                    N_x_t.append(v_r_c)
        if len(N_x_t) == 0:
            N_x_t.append(1)
        return N_x_t

    #Функция обновления ключа для данного временного интервала t
    def UKeyGen(self, t, x, ST_x, RL_x_t, GPP, MSK_fi_x, H_d):
        #Нахождение узлов пользователей для отзыва атрибута
        RL = []
        for user in RL_x_t[x]:
            for l in ST_x['list']:
                if l[0] == user:
                    RL.append(l[1])
        #Вычисление мин кол-ва узлов покрывающих не отозванных пользователей
        N_x_t = self.KUNodes(ST_x, RL)

        Exp = {}
        E, _E = 0, 0
        UK_x_t = {}

        #Для каждого полученного узла генерируется случайная экспонента и вычисляется часть UK
        for v_x in N_x_t:
            UK_x_t[v_x] = {}
            Exp[t] = {v_x: group.random(ZR)}
            UK_x_t[v_x]['E'] = MSK_fi_x['Rx'][v_x] * H_d(x, t) ** Exp[t][v_x]
            UK_x_t[v_x]['_E'] = GPP['g'] ** Exp[t][v_x]
        return UK_x_t

    #Функция вычисления DK
    #На вход SK пользователя для атрибута x, UK для для атрибута x и временного интервала t
    def DKeyCom(self, SK_gid_x, UK_x_t):
        #Нахождение узла принадлежащего пути до узла (u_x_gid) и N_x_t
        #Это гарантируется функцией KUNodes
        for SK_v_x in SK_gid_x['K_gid_x']:
            for UK_v_x in UK_x_t:
                if SK_v_x == UK_v_x:
                    v_x = SK_v_x
                    return {'D_gid_x_t': SK_gid_x['K_gid_x'][v_x] / UK_x_t[v_x]['E'], '_D_gid_x_t': UK_x_t[v_x]['_E']}
        #Если такого узла не существует, то возвращается False
        return False

    #Функция шифрования
    def Encrypt(self, k, t_l, policy_str, GPP, PK_d):
        s = group.random()
        w = group.init(ZR, 0)
        policy = util.createPolicy(policy_str)
        #Выбираем два случайных вектора
        sshares = util.calculateSharesList(s, policy)
        wshares = util.calculateSharesList(w, policy)
        sshares = dict([(x[0].getAttributeAndIndex(), x[1]) for x in sshares])
        wshares = dict([(x[0].getAttributeAndIndex(), x[1]) for x in wshares])
        C = k * pair(GPP['g'], GPP['g']) ** s
        C1, C2, C3, C4 = {}, {}, {}, {}
        for attr, s_share in sshares.items():
            w_share = wshares[attr]
            k_attr = util.strip_index(attr)
            r_i = group.random(ZR)

            for aa in PK_d:
                if attr in PK_d[aa]:
                    C1[attr] = (pair(GPP['g'], GPP['g']) ** s_share) * (PK_d[aa][k_attr]['e(g,g)^alpha'] ** r_i)
                    C2[attr] = (GPP['g'] ** w_share) * (PK_d[aa][k_attr]['g^betta'] ** r_i)
                    C3[attr] = GPP['g'] ** r_i
                    C4[attr] = PK_d[aa]['H'](k_attr, t_l) ** r_i

            # if attr == 'ONE' or attr == 'TWO':
            #     C1[attr] = (pair(GPP['g'], GPP['g']) ** s_share) * (PK_d['aa1'][k_attr]['e(g,g)^alpha'] ** r_i)
            #     C2[attr] = (GPP['g'] ** w_share) * (PK_d['aa1'][k_attr]['g^betta'] ** r_i)
            #     C3[attr] = GPP['g'] ** r_i
            #     C4[attr] = PK_d['aa1']['H'](k_attr, t_l) ** r_i
            # if attr == 'THREE' or attr == 'FOUR':
            #     C1[attr] = (pair(GPP['g'], GPP['g']) ** s_share) * (PK_d['aa2'][k_attr]['e(g,g)^alpha'] ** r_i)
            #     C2[attr] = (GPP['g'] ** w_share) * (PK_d['aa2'][k_attr]['g^betta'] ** r_i)
            #     C3[attr] = GPP['g'] ** r_i
            #     C4[attr] = PK_d['aa2']['H'](k_attr, t_l) ** r_i

        return {'t_l': t_l, 'C': C, 'C1': C1, 'C2': C2, 'C3': C3, 'C4': C4, 'policy': policy_str}

    #Функция расшифрования
    #{DK_gid_x_t}x->S_gid_t - набор компонентов ключа DK для атрибутов пользователя
    #{PK_d} - набор открытых ключей атрибутирующего центра
    def Decrypt(self, CT, GPP, PK_d, DK_gid_x_t, gid):
        #Создние списка атрибутов пользователя
        usr_attr = list(DK_gid_x_t.keys())
        #Создание объекта политики доступа из строки
        policy = util.createPolicy(CT['policy'])
        #Проверка удовлетворения атрибутов пользователя политике доступа
        pruned = util.prune(policy, usr_attr)
        #Если не соответсвует - возвращаем False
        print(pruned)
        if not pruned:
            return False
        coeffs = util.getCoefficients(policy)
        print(coeffs)
        h_gid = GPP['H'](gid)
        egg_s = 1
        for i in pruned:
            x = i.getAttributeAndIndex()
            y = i.getAttribute()
            if DK_gid_x_t[y] == False:
                return False
            num = CT['C1'][x] * pair(h_gid, CT['C2'][x])
            deg = pair(DK_gid_x_t[y]['D_gid_x_t'], CT['C3'][x]) * pair(DK_gid_x_t[y]['_D_gid_x_t'], CT['C4'][x])
            egg_s *= (num / deg) ** coeffs[x]
        return CT['C'] / egg_s


if __name__=='__main__':
    TCP_IP = 'localhost'
    TCP_PORT = 9001
    BUFFER_SIZE = 1024

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    file_get(socket=s)
    sleep(2)