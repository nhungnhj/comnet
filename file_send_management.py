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

only_server_port = 53934 # chuukei
server_port = 60623 # host contains files

def interact_with_client(client_connect): 
    partial_data_1 = bytearray()
    partial_data_2 = bytearray()
    partial_data_3 = bytearray()
    partial_data_4 = bytearray()
    partial_data_5 = bytearray()
    all_data_1 = bytearray()
    all_data_2 = bytearray()
    all_data_3 = bytearray()
    all_data_4 = bytearray()
    all_data_5 = bytearray()
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
        global partial_data_1
        partial_data_1 = recv_data
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
        global all_data_1
        all_data_1 = got_data
        fserver_socket.close()
        print("すべてのファイルを受信完了")
        messege = "すべてのファイルを受信完了\n"
        client_connect.send(messege.encode())
    elif com == 'DLrelay2' and move == 'PARTIAL':
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
        global partial_data_2
        partial_data_2 = recv_data_partial
        print(recv_data_partial)
        stop_time = time.time()
        relay_server_socket.close()
        recv_time = stop_time - start_time
        send_relay = str(recv_time) + " " + "sec" + "\n"
        client_connect.send(send_relay.encode())
        print(recv_time)
        print("計測時間送信完了")
    elif com == 'DLrelay3' and move == 'PARTIAL':
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
        global partial_data_3
        partial_data_3 = recv_data_partial
        print(recv_data_partial)
        stop_time = time.time()
        relay_server_socket.close()
        recv_time = stop_time - start_time
        send_relay = str(recv_time) + " " + "sec" + "\n"
        client_connect.send(send_relay.encode())
        print(recv_time)
        print("計測時間送信完了")
    elif com == 'DLrelay4' and move == 'PARTIAL':
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
        global partial_data_4
        partial_data_4 = recv_data_partial
        print(recv_data_partial)
        stop_time = time.time()
        relay_server_socket.close()
        recv_time = stop_time - start_time
        send_relay = str(recv_time) + " " + "sec" + "\n"
        client_connect.send(send_relay.encode())
        print(recv_time)
        print("計測時間送信完了")
    elif com == 'DLrelay5' and move == 'PARTIAL':
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
        global partial_data_5
        partial_data_5 = recv_data_partial
        print(recv_data_partial)
        stop_time = time.time()
        relay_server_socket.close()
        recv_time = stop_time - start_time
        send_relay = str(recv_time) + " " + "sec" + "\n"
        client_connect.send(send_relay.encode())
        print(recv_time)
        print("計測時間送信完了")
    elif com == 'DLrelay2' and move == 'ALL':
        relay_server_name = fserver
        relay_server_socket = socket(AF_INET, SOCK_STREAM) #ファイルサーバに接続
        relay_server_socket.connect((relay_server_name, only_server_port))

        send_get_all = "GETrelay2" + " " + "dummy" + " " + "dummy" + " " + fname + " " + key + " " + move + "\n"
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
        global all_data_2
        all_data_2 = got_data
        print("全てのデータを受信2")
        relay_server_socket.close()
        print("全てのファイルを受信完了")
        messege = "すべてのファイルを受信完了\n"
        client_connect.send(messege.encode())
    elif com == 'DLrelay3' and move == 'ALL':
        relay_server_name = fserver
        relay_server_socket = socket(AF_INET, SOCK_STREAM) #ファイルサーバに接続
        relay_server_socket.connect((relay_server_name, only_server_port))

        send_get_all = "GETrelay3" + " " + "dummy" + " " + "dummy" + " " + fname + " " + key + " " + move + "\n"
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
        global all_data_3
        all_data_3 = got_data
        print("全てのデータを受信3")
        relay_server_socket.close()
        print("全てのファイルを受信完了")
        messege = "すべてのファイルを受信完了\n"
        client_connect.send(messege.encode())
    elif com == 'DLrelay4' and move == 'ALL':
        relay_server_name = fserver
        relay_server_socket = socket(AF_INET, SOCK_STREAM) #ファイルサーバに接続
        relay_server_socket.connect((relay_server_name, only_server_port))

        send_get_all = "GETrelay4" + " " + "dummy" + " " + "dummy" + " " + fname + " " + key + " " + move + "\n"
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
        global all_data_4
        all_data_4 = got_data
        print("全てのデータを受信4")
        relay_server_socket.close()
        print("全てのファイルを受信完了")
        messege = "すべてのファイルを受信完了\n"
        client_connect.send(messege.encode())
    elif com == 'DLrelay5' and move == 'ALL':
        relay_server_name = fserver
        relay_server_socket = socket(AF_INET, SOCK_STREAM) #ファイルサーバに接続
        relay_server_socket.connect((relay_server_name, only_server_port))

        send_get_all = "GETrelay5" + " " + "dummy" + " " + "dummy" + " " + fname + " " + key + " " + move + "\n"
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
        global all_data_5
        all_data_5 = got_data
        print("全てのデータを受信4")
        relay_server_socket.close()
        print("全てのファイルを受信完了")
        messege = "すべてのファイルを受信完了\n"
        client_connect.send(messege.encode())
    else:
        print(code301)
        
    if com == 'GETrelay' and move == 'PARTIAL':
        print("一部データを送信")
        client_connect.send(partial_data_1)
    elif com == 'GETrelayX' and move == 'PARTIAL':
        print("GETrelayX PARTIAL")
        if "partial_data_1" in globals():
            print("partial_data_1を送信")
            client_connect.send(partial_data_1)
        elif "partial_data_2" in globals():
            print("partial_data_2を送信")
            client_connect.send(partial_data_2)
        elif "partial_data_3" in globals():
            print("partial_data_3を送信")
            client_connect.send(partial_data_3)
        elif "partial_data_4" in globals():
            print("partial_data_4を送信")
            client_connect.send(partial_data_4)
        elif "partial_data_5" in globals():
            print("partial_data_5を送信")
            client_connect.send(partial_data_5)
    elif com == 'GETrelay2' and move == 'ALL':
        print("全てのデータを送信")
        client_connect.send(all_data_1)
    elif com == 'GETrelay3' and move == 'ALL':
        print("全てのデータを送信")
        client_connect.send(all_data_2)
    elif com == 'GETrelay4' and move == 'ALL':
        print("全てのデータを送信")
        client_connect.send(all_data_3)
    elif com == 'GETrelay5' and move == 'ALL':
        print("全てのデータを送信")
        client_connect.send(all_data_4)
    elif com == 'GETrelayX' and move == 'ALL':
        print("GETrelayX ALL")
        if "all_data_1" in globals():
            print("all_data_1を送信")
            client_connect.send(all_data_1)
        elif "all_data_2" in globals():
            print("all_data_2を送信")
            client_connect.send(all_data_2)
        elif "all_data_3" in globals():
            print("all_data_3を送信")
            client_connect.send(all_data_3)
        elif "all_data_4" in globals():
            print("all_data_4を送信")
            client_connect.send(all_data_4)
        elif "all_data_5" in globals():
            print("all_data_5を送信")
            client_connect.send(all_data_5)

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
        ###
