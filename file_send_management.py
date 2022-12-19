# -*- coding: utf-8 -*-
# chuukei
import random
from socket import *
import threading
import pbl2
import time
import subprocess
# key = pbl2.genkey(token)
codeOK = "OK" 
code101 = "NG 101 No such file"     #ファイルが存在しない
code102 = "NG 102 Invalid range"    #指定されたファイルの範囲が不適
code301 = "NG 301 INvalid command"  #コマンドが間違っている

only_server_port = 53922 # chuukei
server_port = 60623 # host contains files

def ping_comd(fileserver):
    r=subprocess.run(["ping", "-c 10", fileserver], stdout=subprocess.PIPE)
    std_out=r.stdout.decode()
    # print(std_out)
    std_out_lst = std_out.split()
    
    if not len(std_out_lst) == 10:
        for word in std_out_lst:
            if word == 'packet':
                word_index = std_out_lst.index(word)
                loss=std_out_lst[word_index-1] # string xx%
                loss=float(loss.split("%")[0]) #float xx [%]
            elif word == 'min/avg/max/mdev':
                word_index = std_out_lst.index(word)
                delay=float(std_out_lst[word_index+2].split("/")[1])/2 #delay float [ms]
                delay = round(delay,0) #delay -> .0f
    else:
        loss = 100
        delay = 0
    return delay, loss

def rep(fserver_name, fname, key, got_data):
    #try: #rep
    fserver_socket = socket(AF_INET, SOCK_STREAM)
    fserver_socket.connect((fserver_name, server_port))
    fil = open(fname, 'w')
    fil.write(got_data.decode())
    repkey_out = pbl2.repkey(key, fname)
    rep = "REP" + " " + fname + " " + repkey_out + "\n"
    fserver_socket.send(rep.encode())
    recv_bytearray = bytearray()
    while True:
        recv_rep = fserver_socket.recv(1)[0]
        recv_bytearray.append(recv_rep)
        if recv_rep == 0x0a:
            break
    print('From Server: {0}'.format(recv_bytearray.decode()))
    #except:
    #    print("Unexpected Error")

def interact_with_client(client_connect): 
    while True:
        receive(client_connect) #クライアントからの命令を実行

    client_connect.close()   

def receive(client_connect):
    sentence = client_connect.recv(1024).decode() #クライアントから命令を受け取る
    print("DLコマンド受信")
    arr = sentence.split()  #単語に分ける
    print(arr)

    com = arr[0]
    fserver = arr[2]
    fname = arr[3]
    key = arr[4]
    move = arr[5]

    if com == 'DL' and move == 'PARTIAL': #クライアントからDLを受け取ったら(PARTIAL)
        fserver_name = fserver
        fserver_socket = socket(AF_INET, SOCK_STREAM) #ファイルサーバに接続
        fserver_socket.connect((fserver_name, server_port)) 

        send_get_partial = "GET" + " " + fname + " " + key + " " + move + " " + arr[6] + " " + arr[7] + "\n"
        #GET_ファイル名_key_PARTIAL_0_9\n
        
        fserver_socket.send(send_get_partial.encode()) #GET要求
        print("GET要求送信")

        start_time = time.time() #受信時間の計測開始
        recv_bytearray = bytearray() #バイト列を格納する配列
        recv_get = bytearray()
        recv_data = bytearray()

        while True:
            recv_get = fserver_socket.recv(1)[0] #ファイルサーバから応答を受け取る
            recv_bytearray.append(recv_get)
            if recv_get == 0x0a:
                break
        recv_data = fserver_socket.recv(int(arr[7])) #指定したバイト数受け取る
        
        stop_time = time.time() #計測終了
        fserver_socket.close() #ファイルサーバから切断
        recv_time = stop_time - start_time #受け取るのにかかった時間を計算
        send_relay = str(recv_time) + " " + "sec" + "\n"
        client_connect.send(send_relay.encode()) #時間をクライアントに送信
        print(recv_time)
        print("計測時間送信完了")

    elif com == 'DL' and move == 'ALL':  #クライアントからDLを受け取ったら(ALL)
        fserver_name = fserver
        fserver_socket = socket(AF_INET, SOCK_STREAM) #ファイルサーバに接続
        fserver_socket.connect((fserver_name, server_port))

        send_get_all = "GET" + " " + fname + " " + key + " " + move + "\n"
        #GET_ファイル名_key_ALL\n

        fserver_socket.send(send_get_all.encode())  #GET要求

        recv_bytearray = bytearray() 
        recv_get_all = bytearray()
        recv_data = bytearray()
        got_data = bytearray()
        while True:
            recv_get_all = fserver_socket.recv(1)[0] #ファイルサーバから応答を受け取る
            recv_bytearray.append(recv_get_all)
            if recv_get_all == 0x0a:
                break
        while True:
            recv_data = fserver_socket.recv(1024)
            got_data += recv_data
            if len(recv_data) <= 0:
                break
        fserver_socket.close()
        #rep(fserver_name, fname, key, got_data)
        client_connect.send(got_data)
        print("すべてのファイルを転送完了")
    else:
        print(code301) 
            

if __name__ == '__main__':
    server_socket = socket(AF_INET, SOCK_STREAM)  # TCPを使う待ち受け用のソケットを作る
    server_socket.bind(('', only_server_port))  # ポート番号をソケットに対応づける
    server_socket.listen(5)  # クライアントからの接続を待つ
    print('The chuukei server is ready to receive')
    while True:
        connection_socket, addr = server_socket.accept()
        client_handler = threading.Thread(target=interact_with_client, args=(connection_socket,))
        client_handler.start() 
