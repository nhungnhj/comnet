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
relay_server_name_list=['pg1','pg2','pg3','pg4','pg5','pg6','pg7']
def ping_comd(fileserver):
    r=subprocess.run(["ping", "-c 6", fileserver], stdout=subprocess.PIPE)
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

def interact_with_client(client_connect): 
    while True:
        receive(client_connect) #クライアントからの命令を実行

    client_connect.close()   

def receive(client_connect):
    sentence = client_connect.recv(1024).decode() #クライアントから命令を受け取る
    #print("DLコマンド受信")
    arr = sentence.split()  #単語に分ける
    print(arr)

    #com = arr[0]
    #fserver = arr[2]
    #fname = arr[3]
    #key = arr[4]
    #move = arr[5]
    """
    if arr[0] in relay_server_name_list:
        server_name= arr[0]
    if arr[0] == 'PING':
        delay, loss= ping_comd(server_name)
"""
    if arr[0]=='GET' or arr[0]=='REP' or arr[0]=='SIZE':
        fserver_name = fserver
        fserver_socket = socket(AF_INET, SOCK_STREAM) #ファイルサーバに接続
        fserver_socket.connect((fserver_name, server_port)) 
        fserver_socket.send(sentence.encode()) #GET要求
        print("GET要求送信")
        server_dat=bytearray()
        while True:
            recv_data=fserver_socket.recv(1024)
            if len(recv_data)<=0:
                break
            server_dat= server_dat + recv_data
        fserver_socket.close()

    if arr[0]=='PING':
        delay, loss= ping_comd(server_name)
        print('遅延',delay, 'ms')
        print('pk loss', loss, '%')
        fserver_socket.send(str(loss).encode())             

if __name__ == '__main__':
    server_socket = socket(AF_INET, SOCK_STREAM)  # TCPを使う待ち受け用のソケットを作る
    server_socket.bind(('', only_server_port))  # ポート番号をソケットに対応づける
    server_socket.listen(10)  # クライアントからの接続を待つ
    print('The chuukei server is ready to receive')
    while True:
        connection_socket, addr = server_socket.accept()
        client_handler = threading.Thread(target=interact_with_client, args=(connection_socket,))
        client_handler.start() 
