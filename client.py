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
# my_server_name = sys.argv[5]
key = pbl2.genkey(token)
only_server_port = 50306

def get_all():
    client_socket= socket(AF_INET,SOCK_STREAM)
    client_socket.connect((server_name,server_port))
    mess="GET {0} {1} ALL\n".format(filename, key)
    client_socket.send(mess.encode())
    recv_bytearray= bytearray()
    while True:
        d=client_socket.recv(1)[0]
        recv_bytearray.append(d)
        if d== 0x0a:
            recv_str=recv_bytearray.decode()
            break
    rep_recv=recv_str.split()
    with open(filename, 'wb') as f:
        while True:
            dat= client_socket.recv(1024)
            if len(dat)<=0:
                break
            f.write(dat)
    client_socket.close()
#ok

def get_partial(saisho,saigo):
    client_socket= socket(AF_INET,SOCK_STREAM)
    client_socket.connect((server_name,server_port))
    mess="GET {0} {1} PARTIAL {2} {3}\n".format(filename, key, saisho,saigo)
    client_socket.send(mess.encode())
    recv_bytearray= bytearray()
    while True:
        d=client_socket.recv(1)[0]
        recv_bytearray.append(d)
        if d== 0x0a:
            recv_str=recv_bytearray.decode()
            break
    rep_recv=recv_str.split()
    with open(filename, 'wb') as f:
        while True:
            dat= client_socket.recv(1024)
            if len(dat)<=0:
                break
            f.write(dat)
    client_socket.close()
#ok

def rep():
    repkey_out= pbl2.repkey(key, filename)
    client_socket=socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_name, server_port))
    rep="REP {0}{1}\n".format(filename, repkey_out)
    client_socket.send(rep.encode())
    client_socket.send(target.encode())
    rep_recv=client_socket.recv(1024)
    rep_recv= rep_recv.decode()
    client_socket.close()
#ok



def size():
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_name, server_port))
    size = "SIZE {}\n".format(file_name) 
    client_socket.send(size.encode())
    recv_bytearray = bytearray()
    #print(size)
    rep_recv=client_socket.recv(1024)
    rep_recv= rep_recv.decode()
    #print(rep_recv)
    client_socket.close()
#ok


if __name__ == '__main__':
    best_time = 1000000
    chuukei_list=['pg1','pg2','pg3','pg4','pg5','pg6','pg7']
    for chuukei_name in chuukei_list:
        if chuukei_name == server_name:
            continue
        client_socket = socket(AF_INET, SOCK_STREAM) #中継サーバに接続
        client_socket.connect((chuukei_name, server_port))
            






if __name__ == '__main__':
    SIZE = size()
    # データを受け取る 
    best_time = 1000000
    #if byte_size[2] > 10000:
    for i in range(1,8):
        relay_server_name = "pg" + str(i) #接続するサーバの選択
        if relay_server_name == server_name or relay_server_name == my_server_name: 
            i=i+1 # 中継サーバとファイルサーバが同じとき飛ばす
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
