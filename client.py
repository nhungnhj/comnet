# client.py

from socket import *
import time
import sys
import pbl2
import subprocess

server_name = sys.argv[1]
server_port = int(sys.argv[2])
file_name = sys.argv[3]
token = sys.argv[4]
my_server_name = sys.argv[5]
key = pbl2.genkey(token)
only_server_port = 53922

def size():
    i = 0
    byte = 0
    try: #try
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((server_name, server_port))
        size = "SIZE" + " " + file_name + "\n"
        client_socket.send(size.encode())
        recv_bytearray = bytearray()
        while True:
            recv_size = client_socket.recv(1)[0]
            recv_bytearray.append(recv_size)
            i += 1
            if recv_size == 0x0a:
                break
        print('From Server: {0}'.format(recv_bytearray.decode()))
        byte_size = recv_bytearray.decode().split()
        return byte_size[2]
    except: 
        print("Unexpected Error")

'''
try: #get(ALL)
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_name, server_port))
    get = "GET" + " " + file_name + " " + key + " " + "ALL\n"
    client_socket.send(get.encode())
    recv_bytearray = bytearray()
    got_data = bytearray()
    while True:
        recv_get = client_socket.recv(1)[0]
        recv_bytearray.append(recv_get)
        if recv_get == 0x0a:
            break
    while True:
        recv_data = client_socket.recv(1024)
        got_data += recv_data
        if len(recv_data) <= 0:
            break
    print('From Server: {0}'.format(recv_bytearray.decode()))
    #print('From Server: {0}'.format(got_data.decode()))
except:
    print("Unexpected Error")
'''

'''
try: #get(partial)
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_name, server_port))
    partial_get = "GET" + " " + file_name + " " + key + " " + "PARTIAL" + " " + str(0) + " " + str(9) + "\n"
    client_socket.send(partial_get.encode())
    recv_bytearray = bytearray()
    while True:
        recv_partial_get = client_socket.recv(1)[0]
        recv_bytearray.append(recv_partial_get)
        if recv_partial_get == 0x0a:
            break
        
    recv_partial_data = client_socket.recv(9)
    print('From Server: {0}'.format(recv_bytearray.decode()))
    print('From Server: {0}'.format(recv_partial_data.decode()))
except:
    print("Unexpected Error")
'''


def recv_ping(chuukei_name):
    client_socket= socket(AF_INET, SOCK_STREAM)
    client_socket.connect((chuukei_name, only_server_port))
    pingcmd = "PING {0} {1}\n".format(chuukei_name, server_name)
    print(pingcmd)
    client_socket.send(pingcmd.encode())
    rep_recv=client_socket.recv(1024)
    rep_recv=rep_recv.decode()
    loss = float(rep_recv)
    print('packet loss:', rep_recv, '%')
    client_socket.close()
    return loss

def rep(got_data):
    try: #rep
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((server_name, server_port))
        fil = open(file_name, 'w')
        fil.write(got_data.decode())
        repkey_out = pbl2.repkey(key, file_name)
        rep = "REP" + " " + file_name + " " + repkey_out + "\n"
        client_socket.send(rep.encode())
        recv_bytearray = bytearray()
        while True:
            recv_rep = client_socket.recv(1)[0]
            recv_bytearray.append(recv_rep)
            if recv_rep == 0x0a:
                break
        print('From Server: {0}'.format(recv_bytearray.decode()))
    except:
        print("Unexpected Error")

if __name__ == '__main__':
    SIZE = size()
    # データを受け取る 
    best_time = 1000000
    #if byte_size[2] > 10000:
    for i in range(1,8):
        relay_server_name = "pg" + str(i) #接続するサーバの選択
        if relay_server_name == server_name: 
            continue # 中継サーバとファイルサーバが同じとき飛ばす
        if relay_server_name == my_server_name:
            continue # 中継サーバとクライアントサーバが同じとき飛ばす
        client_socket = socket(AF_INET, SOCK_STREAM) #中継サーバに接続
        client_socket.connect((relay_server_name, only_server_port)) 
       
        relay_1 = "DL" + " " + relay_server_name + " " + server_name + " " + file_name + " " + key + " " + "PARTIAL" + " " + str(0) + " " + str(9) + "\n"
        #DL_中継サーバ名_ファイルサーバ名_ファイル名_key_partial_0_10\n
        client_socket.send(relay_1.encode()) #中継サーバに送信
        got_relay_1 = bytearray()
        print("応答の受け取り開始")
        while True:
            recv_relay_1 = client_socket.recv(1)[0] #応答を受け取る
            got_relay_1.append(recv_relay_1)
            if recv_relay_1 == 0x0a:
                break

        print("応答の受け取り")

        print('From Server: {} {}'.format(relay_server_name, got_relay_1.decode()))
        spl = got_relay_1.decode().split()
        relay_time = float(spl[0]) #受け取った時間を実数に変換
        pk_loss=recv_ping(relay_server_name)
        if pk_loss==0:
            if relay_time < best_time: #より速い経路が見つかったら更新
                best_time = relay_time 
                best_server = i
    print('From Server: {0}'.format(best_time))
    print('From Server: {0}'.format(best_server))
    best_server_name = "pg" + str(best_server)
    client_socket.close()

    client_socket = socket(AF_INET, SOCK_STREAM) #中継サーバに接続
    client_socket.connect((best_server_name, only_server_port)) 
    relay_2 = "DL" + " " + "pg" + str(best_server) + " " + server_name + " " + file_name + " " + key + " " + "ALL" + "\n"
    client_socket.send(relay_2.encode())
    print("DLコマンド送信(ALL)")
    got_relay_2 = bytearray()
    while True:
        recv_relay_2 = client_socket.recv(1024) #応答を受け取る
        got_relay_2 += recv_relay_2
        if len(got_relay_2) == int(SIZE):
            break
    rep(got_relay_2)
    print("REP要求完了")

    client_socket.close() 
