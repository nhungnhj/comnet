# -*- coding: utf-8 -*-
# chuukei 
import random
from socket import *
import threading
import pbl2
import time

codeOK = "OK" 
code101 = "NG 101 No such file"     #ファイルが存在しない
code102 = "NG 102 Invalid range"    #指定されたファイルの範囲が不適
code301 = "NG 301 INvalid command"  #コマンドが間違っている

only_server_port = 53939 # chuukei
server_port = 60623 # host contains files

def rep(fserver_name, fname, key, got_data):
    #try: #rep
    fserver_socket = socket(AF_INET, SOCK_STREAM)
    fserver_socket.connect((fserver_name, server_port))
    fil = open(fname, 'wb')
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
    partial_data = bytearray()
    all_data = bytearray()
    while True:
        receive(client_connect) #クライアントからの命令を実行

def receive(client_connect):
    sentence = client_connect.recv(1024).decode()
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
        global partial_data
        partial_data = recv_data
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
        global all_data
        all_data = got_data
        fserver_socket.close()
        #rep(fserver_name, fname, key, got_data)
        #client_connect.send(got_data)
        print("すべてのファイルを受信完了")
        messege = "すべてのファイルを受信完了\n"
        client_connect.send(messege.encode())
    elif com == 'DLrelay' and move == 'PARTIAL':
        relay_server_name = fserver
        relay_server_socket = socket(AF_INET, SOCK_STREAM)
        relay_server_socket.connect((relay_server_name, only_server_port))

        send_get_partial = "GETrelay" + " " + "dummy" + " " + "dummy" + " " + fname + " " + key + " " + move + " " + str(0) + " " + str(9) + "\n"
        #GETrelay_dummy_dummy_ファイル名_key_partial_0_9\n
        relay_server_socket.send(send_get_partial.encode())
        print("GET要求送信")
        recv_data_partial = bytearray()
        start_time = time.time()
        recv_data_partial = relay_server_socket.recv(int(arr[7]))
        print(recv_data_partial)
        stop_time = time.time()
        relay_server_socket.close()
        recv_time = stop_time - start_time
        send_relay = str(recv_time) + " " + "sec" + "\n"
        client_connect.send(send_relay.encode())
        print(recv_time)
        print("計測時間送信完了")
    elif com == 'DLrelay' and move == 'ALL':
        relay_server_name = fserver
        relay_server_socket = socket(AF_INET, SOCK_STREAM) #ファイルサーバに接続
        relay_server_socket.connect((relay_server_name, only_server_port))

        send_get_all = "GETrelay" + " " + "dummy" + " " + "dummy" + " " + fname + " " + key + " " + move + "\n"
        #GETrelay_dummy_dummy_ファイル名_key_ALL\n
        relay_server_socket.send(send_get_all.encode())
        print("GET要求送信")

        recv_data = bytearray()
        got_data = bytearray()
        while True:
            recv_data = relay_server_socket.recv(1024)
            got_data += recv_data
            if len(recv_data) <= 0:
                break
        print("全てのデータを受信2")
        relay_server_socket.close()
        client_connect.send(got_data)
        print("クライアントにファイルを送信")
    else:
        print(code301)
        
    if com == 'GETrelay' and move == 'PARTIAL':
        print("一部データを送信")
        client_connect.send(partial_data)
    elif com == 'GETrelay' and move == 'ALL':
        print("全てのデータを送信")
        client_connect.send(all_data)

    client_connect.close()
    
if __name__ == '__main__':
    server_socket = socket(AF_INET, SOCK_STREAM)  # TCPを使う待ち受け用のソケットを作る
    server_socket.bind(('', only_server_port))  # ポート番号をソケットに対応づける
    server_socket.listen(5)  # クライアントからの接続を待つ
    print('The chuukei server is ready to receive')
    while True:
        connection_socket, addr = server_socket.accept()
        client_handler = threading.Thread(target=interact_with_client, args=(connection_socket,))
        client_handler.start()
