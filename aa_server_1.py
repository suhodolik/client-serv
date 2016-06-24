# coding: utf-8

from charm.toolbox.pairinggroup import G1, G2, GT, PairingGroup, ZR, pair
from charm.toolbox.secretutil import SecretUtil
from Crypto.Hash import MD5
import charm.core.engine.util as utils

from server import Server



class AA_server(Server):
    def __init__(self, port, count, groupObj, GPP, attributes):
        self._groupObj = groupObj
        self._taac = TAAC(groupObj=groupObj)
        self._time_t = 1
        self._GPP = GPP
        self._AAs = self._taac.AuthoritySetup(GPP=self._GPP, U=attributes)
        self.attributes = attributes
        self._users = {}
        self._SK = {}
        Server.__init__(port=port, count=count)

    def prepare_user_keys(self, user_name, user_attributes):  # user_name='user_1', user_attributes=['ONE', 'TWO', 'SIX']
        self._users[user_name] = user_attributes
        self._SK[user_name] = {}

        for attr in user_attributes:
            if attr in self.attributes:
                self._SK[user_name][attr] = self._taac.SKeyGen(gid=user_name,
                                                         x=attr,
                                                         ST_x=self._AAs['ST'][attr],
                                                         GPP=self._GPP,
                                                         MSK_fi_x=self._AAs['MSK'][attr])

    def send_public_keys(self):
        pass

    def encode_data(self, data):
        return utils.objectToBytes(data, self._groupObj)

    def decode_data(self, data):
        return utils.bytesToObject(data, self._groupObj)


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


if __name__ == "__main__":
    groupObj = PairingGroup('SS512')
    taac_obj_gpp = TAAC(groupObj=groupObj)
    GPP = taac_obj_gpp.GlobalSetup()


    AA_1 = AA_server(port=14001, count=1, groupObj=groupObj)

    AA_2 = AA_server(port=14002, count=1, groupObj=groupObj)
