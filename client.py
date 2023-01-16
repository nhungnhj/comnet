# client.py

from socket import *
import time
import sys
import pbl2

server_name = sys.argv[1]
server_port = int(sys.argv[2])
file_name = sys.argv[3]
token = sys.argv[4]
my_server_name = sys.argv[5]
key = pbl2.genkey(token)
only_server_port = 53934

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


def rep(got_data):
    try: #rep
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((server_name, server_port))
        if type(got_data) == str:
            fil = open(file_name, 'w')
            fil.write(got_data.decode())
        else:
            fil = open(file_name, 'wb')
            fil.write(got_data)
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
    # 第1段階 ---------------------------------------------------- 
    best_time = 100
    for i in range(1,8):
        relay_server_name = "pg" + str(i) #接続するサーバの選択
        if relay_server_name == server_name: 
            continue # 中継サーバとファイルサーバが同じとき飛ばす
        if relay_server_name == my_server_name:
            continue # 中継サーバとクライアントサーバが同じとき飛ばす
        client_socket = socket(AF_INET, SOCK_STREAM) #中継サーバに接続
        client_socket.connect((relay_server_name, only_server_port)) 
        relay = "DL" + " " + relay_server_name + " " + server_name + " " + file_name + " " + key + " " + "PARTIAL" + " " + str(0) + " " + str(99) + "\n"
        #DL_中継サーバ名_ファイルサーバ名_ファイル名_key_partial_0_10\n
        try: # 5秒以内に実行できない場合except文に移る
            client_socket.settimeout(2.0)
            client_socket.send(relay.encode()) #中継サーバに送信
            got_relay = bytearray()
            print("応答の受け取り開始")
            while True:
                recv_relay = client_socket.recv(1)[0] #応答を受け取る
                got_relay.append(recv_relay)
                if recv_relay == 0x0a:
                    break
            print("応答の受け取り")
            print('From Server: {} {}'.format(relay_server_name, got_relay.decode()))
            client_socket.settimeout(None)
            spl = got_relay.decode().split()
            relay_time = float(spl[0]) #受け取った時間を実数に変換
        except:
            relay_time = 2.0
            print('From Server: {} {}'.format(relay_server_name, relay_time))
            client_socket.close()
        finally:
            if relay_time < best_time: #より速い経路が見つかったら更新
                best_time = relay_time 
                best_server = i
            client_socket.close()
    print('From Server: {0}'.format(best_time))
    print('From Server: {0}'.format(best_server))
    best_server_name = "pg" + str(best_server)

    client_socket = socket(AF_INET, SOCK_STREAM) #中継サーバに接続
    client_socket.connect((best_server_name, only_server_port)) 
    relay = "DL" + " " + "pg" + str(best_server) + " " + server_name + " " + file_name + " " + key + " " + "ALL" + "\n"
    client_socket.send(relay.encode())
    print("DLコマンド送信(ALL)")
    got_relay = bytearray()
    while True:
        recv_relay = client_socket.recv(1)[0]
        got_relay.append(recv_relay) 
        if recv_relay == 0x0a:
            break
    explored_server_1 = best_server #ファイルを受け取ったサーバを記憶
    print(got_relay.decode())
    client_socket.close()

    # 第2段階 ---------------------------------------------------
    best_time = 100
    for i in range(1,8):
        relay_server_name = "pg" + str(i)
        if relay_server_name == server_name:
            continue
        if relay_server_name == my_server_name:
            continue
        if i == explored_server_1:
            continue
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((relay_server_name, only_server_port))
        relay = "DLrelay2" + " " + relay_server_name + " " + best_server_name + " " + file_name + " " + key + " " + "PARTIAL" + " " + str(0) + " " + str(99) + "\n"
        #DLrelay_中継サーバ名_ファイルサーバ名(中継サーバ)_ファイル名_key_partial_0_9\n
        try:
            client_socket.settimeout(2.0)
            client_socket.send(relay.encode())
            got_relay = bytearray()
            print("応答の受け取り開始")
            while True:
                recv_relay = client_socket.recv(1)[0] #応答を受け取る
                got_relay.append(recv_relay)
                if recv_relay == 0x0a:
                    break
            print("応答の受け取り")
            print('From Server: {} {}'.format(relay_server_name, got_relay.decode()))
            client_socket.settimeout(None)
            spl = got_relay.decode().split()
            relay_time = float(spl[0]) #受け取った時間を実数に変換
        except:
            relay_time = 2.0
            print('From Server: {} {}'.format(relay_server_name, relay_time))
            client_socket.close()
        finally:
            if relay_time < best_time: #より速い経路が見つかったら更新
                best_time = relay_time 
                best_server = i
            client_socket.close()
    print('From Server: {0}'.format(best_time)) 
    print('From Server: {0}'.format(best_server))
    best_server_name = "pg" + str(best_server)

    client_socket = socket(AF_INET, SOCK_STREAM) #中継サーバに接続
    client_socket.connect((best_server_name, only_server_port)) 
    relay = "DLrelay2" + " " + "pg" + str(best_server) + " " + "pg" + str(explored_server_1) + " " + file_name + " " + key + " " + "ALL" + "\n"
    client_socket.send(relay.encode())
    print("DLコマンド送信(ALL)")
    got_relay = bytearray()
    while True:
        recv_relay = client_socket.recv(1)[0]
        got_relay.append(recv_relay) 
        if recv_relay == 0x0a:
            break
    explored_server_2 = best_server #ファイルを受け取ったサーバを記憶
    print(got_relay.decode())
    client_socket.close()

    # 第3段階 ----------------------------------------------------
    best_time = 100
    for i in range(1,8):
        relay_server_name = "pg" + str(i)
        if relay_server_name == server_name:
            continue
        if relay_server_name == my_server_name:
            continue
        if i == explored_server_1:
            continue
        if i == explored_server_2:
            continue
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((relay_server_name, only_server_port))
        relay = "DLrelay3" + " " + relay_server_name + " " + best_server_name + " " + file_name + " " + key + " " + "PARTIAL" + " " + str(0) + " " + str(99) + "\n"
        #DLrelay_中継サーバ名_ファイルサーバ名(中継サーバ)_ファイル名_key_partial_0_9\n
        try:
            client_socket.settimeout(2.0)
            client_socket.send(relay.encode())
            got_relay = bytearray()
            print("応答の受け取り開始")
            while True:
                recv_relay = client_socket.recv(1)[0] #応答を受け取る
                got_relay.append(recv_relay)
                if recv_relay == 0x0a:
                    break
            print("応答の受け取り")
            print('From Server: {} {}'.format(relay_server_name, got_relay.decode()))
            client_socket.settimeout(None)
            spl = got_relay.decode().split()
            relay_time = float(spl[0]) #受け取った時間を実数に変換
        except:
            relay_time = 2.0
            print('From Server: {} {}'.format(relay_server_name, relay_time))
            client_socket.close()
        finally:
            if relay_time < best_time: #より速い経路が見つかったら更新
                best_time = relay_time 
                best_server = i
            client_socket.close()
    print('From Server: {0}'.format(best_time)) 
    print('From Server: {0}'.format(best_server))
    best_server_name = "pg" + str(best_server)
    client_socket = socket(AF_INET, SOCK_STREAM) #中継サーバに接続
    client_socket.connect((best_server_name, only_server_port)) 
    relay = "DLrelay3" + " " + "pg" + str(best_server) + " " + "pg" + str(explored_server_2) + " " + file_name + " " + key + " " + "ALL" + "\n"
    client_socket.send(relay.encode())
    print("DLコマンド送信(ALL)")
    got_relay = bytearray()
    while True:
        recv_relay = client_socket.recv(1)[0]
        got_relay.append(recv_relay) 
        if recv_relay == 0x0a:
            break
    explored_server_3 = best_server #ファイルを受け取ったサーバを記憶
    print(got_relay.decode())
    client_socket.close()

    # 第4段階 ---------------------------------------------------
    best_time = 100
    for i in range(1,8):
        relay_server_name = "pg" + str(i)
        if relay_server_name == server_name:
            continue
        if relay_server_name == my_server_name:
            continue
        if i == explored_server_1:
            continue
        if i == explored_server_2:
            continue
        if i == explored_server_3:
            continue
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((relay_server_name, only_server_port))
        relay = "DLrelay4" + " " + relay_server_name + " " + best_server_name + " " + file_name + " " + key + " " + "PARTIAL" + " " + str(0) + " " + str(99) + "\n"
        #DLrelay_中継サーバ名_ファイルサーバ名(中継サーバ)_ファイル名_key_partial_0_9\n
        try:
            client_socket.settimeout(2.0)
            client_socket.send(relay.encode())
            got_relay = bytearray()
            print("応答の受け取り開始")
            while True:
                recv_relay = client_socket.recv(1)[0] #応答を受け取る
                got_relay.append(recv_relay)
                if recv_relay == 0x0a:
                    break
            print("応答の受け取り")
            print('From Server: {} {}'.format(relay_server_name, got_relay.decode()))
            client_socket.settimeout(None)
            spl = got_relay.decode().split()
            relay_time = float(spl[0]) #受け取った時間を実数に変換
        except:
            relay_time = 2.0
            print('From Server: {} {}'.format(relay_server_name, relay_time))
            client_socket.close()
        finally:
            if relay_time < best_time: #より速い経路が見つかったら更新
                best_time = relay_time 
                best_server = i
            client_socket.close()
    print('From Server: {0}'.format(best_time)) 
    print('From Server: {0}'.format(best_server))
    best_server_name = "pg" + str(best_server)
    client_socket = socket(AF_INET, SOCK_STREAM) #中継サーバに接続
    client_socket.connect((best_server_name, only_server_port)) 
    relay = "DLrelay4" + " " + "pg" + str(best_server) + " " + "pg" + str(explored_server_3) + " " + file_name + " " + key + " " + "ALL" + "\n"
    client_socket.send(relay.encode())
    print("DLコマンド送信(ALL)")
    got_relay = bytearray()
    while True:
        recv_relay = client_socket.recv(1)[0]
        got_relay.append(recv_relay) 
        if recv_relay == 0x0a:
            break
    explored_server_4 = best_server #ファイルを受け取ったサーバを記憶
    print(got_relay.decode())
    client_socket.close()

    #第5段階 ---------------------------------------------------
    best_time = 100
    for i in range(1,8):
        relay_server_name = "pg" + str(i)
        if relay_server_name == server_name:
            continue
        if relay_server_name == my_server_name:
            continue
        if i == explored_server_1:
            continue
        if i == explored_server_2:
            continue
        if i == explored_server_3:
            continue
        if i == explored_server_4:
            continue
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((relay_server_name, only_server_port))
        relay = "DLrelay5" + " " + relay_server_name + " " + best_server_name + " " + file_name + " " + key + " " + "PARTIAL" + " " + str(0) + " " + str(99) + "\n"
        #DLrelay_中継サーバ名_ファイルサーバ名(中継サーバ)_ファイル名_key_partial_0_9\n
        try:
            client_socket.settimeout(2.0)
            client_socket.send(relay.encode())
            got_relay = bytearray()
            print("応答の受け取り開始")
            while True:
                recv_relay = client_socket.recv(1)[0] #応答を受け取る
                got_relay.append(recv_relay)
                if recv_relay == 0x0a:
                    break
            print("応答の受け取り")
            print('From Server: {} {}'.format(relay_server_name, got_relay.decode()))
            client_socket.settimeout(None)
            spl = got_relay.decode().split()
            relay_time = float(spl[0]) #受け取った時間を実数に変換
            if relay_time < best_time: #より速い経路が見つかったら更新
                best_time = relay_time 
                best_server = i
            client_socket.close()
            print('From Server: {0}'.format(best_time)) 
            print('From Server: {0}'.format(best_server))
            best_server_name = "pg" + str(best_server)
            client_socket = socket(AF_INET, SOCK_STREAM) #中継サーバに接続
            client_socket.connect((best_server_name, only_server_port)) 
            relay = "DLrelay5" + " " + "pg" + str(best_server) + " " + "pg" + str(explored_server_4) + " " + file_name + " " + key + " " + "ALL" + "\n"
            client_socket.send(relay.encode())
            print("DLコマンド送信(ALL)")
            got_relay = bytearray()
            while True:
                recv_relay = client_socket.recv(1)[0]
                got_relay.append(recv_relay) 
                if recv_relay == 0x0a:
                    break
            print(got_relay.decode())
            client_socket.close()
        except:
            relay_time = 2.0
            print('From Server: {} {}'.format(relay_server_name, relay_time))
            nonexplored_server = i
            client_socket.close()
'''
        finally:
            if relay_time < best_time: #より速い経路が見つかったら更新
                best_time = relay_time 
                best_server = i
            client_socket.close()
    print('From Server: {0}'.format(best_time)) 
    print('From Server: {0}'.format(best_server))
    best_server_name = "pg" + str(best_server)
    client_socket = socket(AF_INET, SOCK_STREAM) #中継サーバに接続
    client_socket.connect((best_server_name, only_server_port)) 
    relay = "DLrelay5" + " " + "pg" + str(best_server) + " " + "pg" + str(explored_server_4) + " " + file_name + " " + key + " " + "ALL" + "\n"
    client_socket.send(relay.encode())
    print("DLコマンド送信(ALL)")
    got_relay = bytearray()
    while True:
        recv_relay = client_socket.recv(1)[0]
        got_relay.append(recv_relay) 
        if recv_relay == 0x0a:
            break
    explored_server_5 = best_server #ファイルを受け取ったサーバを記憶
    print(got_relay.decode())
    client_socket.close()
'''
    # 第6段階 ------------------------------------------------
    best_time = 100
    for i in range(1,8):
        relay_server_name = "pg" + str(i)
        if relay_server_name == server_name:
            continue
        if relay_server_name == my_server_name:
            continue
        if i == nonexplored_server:
            continue
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((relay_server_name, only_server_port))
        relay = "GETrelayX" + " " + "dummy" + " " + "dummy" + " " + file_name + " " + key + " " + "PARTIAL" + " " + str(0) + " " + str(99) + "\n"
        #GETrelay_dummy_dummy_ファイル名_key_partial_0_9\n
        try:
            client_socket.settimeout(2.0)
            client_socket.send(relay.encode())
            recv_relay = bytearray()
            print("応答の受け取り開始")
            start_time = time.time()
            recv_relay = client_socket.recv(99)
            stop_time = time.time()
            relay_time = stop_time - start_time
            print('From Server: {} {}'.format(relay_server_name, relay_time))
            client_socket.settimeout(None)
        except:
            relay_time = 2.0
            print('From Server: {} {}'.format(relay_server_name, relay_time))
            client_socket.close()
        finally:
            if relay_time < best_time: #より速い経路が見つかったら更新
                best_time = relay_time 
                best_server = i
            client_socket.close()
    print('From Server: {0}'.format(best_time)) 
    print('From Server: {0}'.format(best_server))
    best_server_name = "pg" + str(best_server)
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((best_server_name, only_server_port)) 
    relay = "GETrelayX" + " " + "dummy" + " " + "dummy" + " " + file_name + " " + key + " " + "ALL" + "\n"
    client_socket.send(relay.encode())
    print("DLコマンド送信(ALL)")
    recv_data = bytearray()
    got_data = bytearray()
    while True:
        recv_data = client_socket.recv(1024) #応答を受け取る
        got_data += recv_data
        if len(recv_data) <= 0:
            break
    rep(got_data)
    print("REP要求完了") 
    client_socket.close() 
