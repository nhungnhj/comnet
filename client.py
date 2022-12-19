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
only_server_port = 53922

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


def get_all(relay_server_name):
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

def get_partial(relay_server_name,saisho,saigo):
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
    SIZE = size()
    # データを受け取る 
    best_time = 1000000
    best_relay_server_name= ''
    #if byte_size[2] > 10000:
    relay_server_name_list=['pg1','pg2','pg3','pg4','pg5','pg6','pg7']

    start_timing=time.time()
    for relay_server_name in relay_server_name_list: #接続するサーバの選択
        client_socket = socket(AF_INET, SOCK_STREAM) #中継サーバに接続
        client_socket.connect((relay_server_name, only_server_port))
        client_socket.send(server_name.encode())
        client_socket.close()
        #if relay_server_name == server_name: 
         #   continue # 中継サーバとファイルサーバが同じとき飛ばす
        #if relay_server_name == my_server_name:
        #    continue # 中継サーバとクライアントサーバが同じとき飛ばす
        #client_socket = socket(AF_INET, SOCK_STREAM) #中継サーバに接続
        #client_socket.connect((relay_server_name, only_server_port)) 
        
        loss=recv_ping(relay_server_name)
        if loss == 0:
            #relay_1 = "DL" + " " + relay_server_name + " " + server_name + " " + file_name + " " + key + " " + "PARTIAL" + " " + str(0) + " " + str(9) + "\n"
            #DL_中継サーバ名_ファイルサーバ名_ファイル名_key_partial_0_10\n
            #client_socket.send(relay_1.encode()) #中継サーバに送信
            start=time.time()
            get_partial(relay_server_name,0,10000)
            end=time.time()
            #if mess[0]=='GET' or mess[0]=='REP':
            print("throught{0}, download time: {1}\n".format(relay_server_name,end - start))
            if best_time > end - start:
                best_time=end - start
                best_relay_server_name=relay_server_name
    print("best time: {0}\n".format(best_time))
    print("best chuukei server name: {0}\n".format(best_relay_server_name))
    get_all(relay_server_name)
    end_timing=time.time()
    print("best time download file: {0}\n".format(end_timing-start_timing))

    print("REP要求完了")

    #client_socket.close() 
