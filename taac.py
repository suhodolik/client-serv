# coding: utf-8

from charm.toolbox.pairinggroup import G1, G2, GT, PairingGroup, ZR, pair
from charm.toolbox.secretutil import SecretUtil
from Crypto.Hash import MD5
import charm.core.engine.util as utils

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


def test2():
    groupObj = PairingGroup('SS512')
    taac = TAAC(groupObj)

    t = 1

    #Инициализация системы, генерация GPP
    GPP = taac.GlobalSetup()
    #АЦ в системе
    AAs = {}
    #АЦ аа1 управляющий атрибутами ONE, TWO
    AAs['aa1'] = taac.AuthoritySetup(GPP, ['ONE', 'TWO'])
    #АЦ аа2 управляющий атрибутами THREE, FOUR
    AAs['aa2'] = taac.AuthoritySetup(GPP, ['THREE', 'FOUR', 'SIX'])
    all_attr = ['ONE', 'TWO', 'THREE', 'FOUR', 'SIX']
    #print(AAs['aa1'])
    #print(AAs['aa2'])
    #Пользователи в системе
    users = {}
    #Создание пользователей и присвоение им атрибутов
    users['user1'] = ['ONE', 'TWO', 'SIX']
    users['user2'] = ['ONE', 'THREE']
    users['user3'] = ['ONE', 'FOUR']
    users['user4'] = ['TWO', 'THREE']
    users['user5'] = ['TWO', 'FOUR']
    users['user6'] = ['THREE', 'FOUR']

    SK = {}

    #Генерация SK пользователей
    for user in users:
        SK[user] = {}
        for attr in users[user]:
            if attr == 'ONE' or attr == 'TWO':
                SK[user][attr] = taac.SKeyGen(user, attr, AAs['aa1']['ST'][attr], GPP, AAs['aa1']['MSK'][attr])
            else:
                SK[user][attr] = taac.SKeyGen(user, attr, AAs['aa2']['ST'][attr], GPP, AAs['aa2']['MSK'][attr])
        #print(SK[user])
    #print(AAs['aa1']['ST'])
    #print(AAs['aa2']['ST'])

    # SK['user3']['ONE']['SK']['K_gid_x'][1]

    # utils.objectToBytes(SK)
    m = groupObj.random(GT)
    policy = '((ONE or THREE) and (TWO or FOUR))'
    enc_m = taac.Encrypt(m, t, policy, GPP, {'aa1': AAs['aa1']['PK'], 'aa2': AAs['aa2']['PK']})

    #Отзыв у пользователя user1 атрибута ONE
    RL = {'ONE': ['user1'], 'TWO': [], 'THREE': [], 'FOUR': []}


    #Время в программе идет по циклу
    #На каждом временном интервале АЦ вычисляют UK
    #Затем пользователи вычисляют DK
    #Затем пользователи пытаются расшифровать CT

    DK = {}

    for t in range(1, 3):
        print('____________________Временной интервал:', t, '____________________')
        RL = {'ONE': [], 'TWO': [], 'THREE': [], 'FOUR': [], 'SIX': []}
        #На временном интервале t = 2: RL менятеся, у пользователя user1 отзывается атрибут 'ONE'
        if t == 2:
            RL = {'ONE': ['user1'], 'TWO': [], 'THREE': [], 'FOUR': [], 'SIX': []}
        print('RL: ', RL)

        #Генерация ключей обновления для атрибутов
        UK = {}
        for attr in all_attr:
            if attr == 'ONE' or attr == 'TWO':
                UK[attr] = taac.UKeyGen(0, attr, AAs['aa1']['ST'][attr], RL, GPP, AAs['aa1']['MSK'][attr], AAs['aa1']['PK']['H'])
            else:
                UK[attr] = taac.UKeyGen(0, attr, AAs['aa2']['ST'][attr], RL, GPP, AAs['aa2']['MSK'][attr], AAs['aa2']['PK']['H'])
        #DK = {}

        DK[t] = {}

        #Вычисление DK
        print('____________________Вычисление DK____________________')
        for user in users:
            DK[t][user] = {}
            for attr in users[user]:
                DK[t][user][attr] = taac.DKeyCom(SK[user][attr]['SK'], UK[attr])
                if DK[t][user][attr] != False:
                    print(user, attr, ': DK вычислен успешно')
                else:
                    print(user, attr, False)

        #Расшифрование
        print('____________________Расшифрование____________________')
        for user in users:
            print(user)
            print('CT policy:', policy)
            print('User attr:', users[user])
            print('     OT:', m)
            _m = taac.Decrypt(enc_m, GPP, {'aa1': AAs['aa1']['PK'], 'aa2': AAs['aa2']['PK']}, DK[t][user], user)
            print('     Dec CT:', _m)

# def test():
#     t = 0
#     groupObj = PairingGroup('SS512')
#     taac = TAAC(groupObj)
#     GPP = taac.GlobalSetup() #Инициализация системы
#     AAs = {}
#     AAs['aa1'] = taac.AuthoritySetup(GPP, ('ONE', 'TWO'))
#     AAs['aa2'] = taac.AuthoritySetup(GPP, ('THREE', 'FOUR'))
#     all_attr = ['ONE', 'TWO', 'THREE', 'FOUR']
#     attr_user = {'bob': ['ONE', 'TWO'], 'alice': ['THREE', 'FOUR'], 'andrey': ['ONE', 'TWO'], 'evgen': ['TWO', 'FOUR']}
#     SK = {}
#     for user in attr_user:
#         SK[user] = {}
#         for attr in attr_user[user]:
#             if attr == 'ONE' or attr == 'TWO':
#                 SK[user][attr] = taac.SKeyGen(user, attr, AAs['aa1']['ST'][attr], GPP, AAs['aa1']['MSK_d'][attr])
#                 AAs['aa1']['ST'][attr] = SK[user][attr]['ST_x']
#             else:
#                 SK[user][attr] = taac.SKeyGen(user, attr, AAs['aa2']['ST'][attr], GPP, AAs['aa2']['MSK_d'][attr])
#                 AAs['aa2']['ST'][attr] = SK[user][attr]['ST_x']
#     m = groupObj.random(GT)
#     policy = '((ONE or THREE) and (TWO or FOUR))'
#     PK_d_AAs = {}
#     for a, b in zip(AAs['aa1']['PK_d'].keys(), AAs['aa2']['PK_d'].keys()):
#         PK_d_AAs[a] = AAs['aa1']['PK_d'][a]
#         PK_d_AAs[b] = AAs['aa2']['PK_d'][b]
#     enc_m = taac.Encrypt(m, 1, policy, GPP, PK_d_AAs)
#     UK = {}
#     DK = {}
#     for t in range(1, 3):
#         RL = []
#         print('Временной интервал: ', t)
#         UK[t] = {}
#         for attr in all_attr:
#             if t == 2 and attr == 'TWO':
#                 RL = [8]
#                 print(AAs['aa1']['ST'][attr])
#             if attr == 'ONE' or attr == 'TWO':
#                 UK[t][attr] = taac.UKeyGEn(t, attr, AAs['aa1']['ST'][attr], RL, GPP, AAs['aa1']['MSK_d'][attr], AAs['aa1']['H_d'])
#             else:
#                 UK[t][attr] = taac.UKeyGEn(t, attr, AAs['aa2']['ST'][attr], RL, GPP, AAs['aa2']['MSK_d'][attr], AAs['aa2']['H_d'])
#         for user in attr_user:
#             DK[user] = {}
#             for attr in attr_user[user]:
#                     DK[user][attr] = taac.DKeyCom(SK[user][attr]['SK'], UK[t][attr])
#         print(policy)
#         for user in attr_user:
#             print(user, ' - ', attr_user[user])
#             _m = taac.Decrypt(enc_m, GPP, PK_d_AAs, DK[user], user)
#             print(m)
#             print(_m)
#             if _m == m:
#                 print('Success')
#             else:
#                 print('error')

# def main():
#     groupObj = PairingGroup('SS512')
#     taac = TAAC(groupObj)
#     GPP = taac.GlobalSetup()
#     AAs = {}
#     AAs['aa1'] = taac.AuthoritySetup(GPP, ('ONE', 'TWO', 'THREE'))
#     #AAs['aa2'] = taac.AuthoritySetup(GPP, ('THREE', 'FOUR'))
#     #Генерирование секретного ключа пользователя
#     attr_user = ['ONE']
#     SK_u1 = {}
#     for x in attr_user:
#         SK_u1[x] = taac.SKeyGen('bob', x, AAs['aa1']['ST'][x], GPP, AAs['aa1']['MSK_d'][x])
#     AAs['aa1']['ST']['ONE'] = SK_u1['ONE']['ST_x']
#     m = groupObj.random(GT)
#     policy = '(one or three)'
#     enc_msg = taac.Encrypt(m, 1, policy, GPP, AAs['aa1']['PK_d'])
#     UK_u1 = {}
#     for x in attr_user:
#         UK_u1[x] = taac.UKeyGEn(1, x, AAs['aa1']['ST'][x], [], GPP, AAs['aa1']['MSK_d'][x], AAs['aa1']['H_d'])
#     DK_u1 = {}
#     for x in attr_user:
#         DK_u1[x] = taac.DKeyCom(SK_u1[x]['SK'], UK_u1[x])
#     dec = taac.Decrypt(enc_msg, GPP, AAs['aa1']['PK_d'], DK_u1, 'bob')
#     print(m)
#     print(dec)
# test()
if __name__ == "__main__":
    test2()