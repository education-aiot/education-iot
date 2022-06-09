from socket import *
from threading import *
import os
import datetime
import time

#--------------클라이언트 세팅 -----------------------
Host='127.0.0.1' # 서버의 IP주소를 입력하세요.
Port = 9190 # 사용할 포트 번호. 
#---------------------------------------

def now_time(): 
    now = datetime.datetime.now()
    time_str=now.strftime('[%H:%M] ')
    return time_str

def send_func():  # 201)
    while True:
        send_data=input('당신 : ')
        client_sock.send(send_data.encode('utf-8'))
        if send_data=='!quit':
            print('연결을 종료하였습니다.')
            break 
    client_sock.close()
    os._exit(1)

def recv_func(): # 202)
    while True:
        try:
            recv_data=(client_sock.recv(1024)).decode('utf-8')
            if len(recv_data)==0:
                print('[SYSTEM] 서버와의 연결이 끊어졌습니다.')
                client_sock.close()
                os._exit(1)
        except Exception as e:
            print('예외가 발생했습니다.', e) # 예외처리중
            print('[SYSTEM] 메시지를 수신하지 못하였습니다.')
        else:
            print(recv_data)
            pass

client_sock=socket(AF_INET, SOCK_STREAM)
try:
    client_sock.connect((Host,Port))

except ConnectionRefusedError:
    print('서버에 연결할 수 없습니다.')
    print('1. 서버의 ip주소와 포트번호가 올바른지 확인하십시오.')
    print('2. 서버 실행 여부를 확인하십시오.')
    os._exit(1)

except:
    print('프로그램을 정상적으로 실행할 수 없습니다. 프로그램 개발자에게 문의하세요.')

else:
    print('[SYSTEM] 서버와 연결되었습니다.')

while True:
    name = input('사용하실 닉네임을 입력하세요 :')   # 0)  
    if ' ' in name:
        print('공백은 입력이 불가능합니다.')
        continue
    client_sock.send(name.encode()) # 101) 이름 전송
    is_possible_name=client_sock.recv(1024).decode()  # 102) 이름 수신
    
    if is_possible_name=='yes':                  # 1) 이름 중복 없을 시 while   >>> (멈춤)
        print(now_time()+ '채팅방에 입장하였습니다.')
        client_sock.send('!enter'.encode())
        break

    elif is_possible_name=='overlapped':         # 1) while(1)
        print('[SYSTEM] 이미 사용중인 닉네임입니다.')

sender=Thread(target=send_func, args=())          # 201) 
receiver=Thread(target=recv_func, args=())        # 202) 
sender.start()
receiver.start()

while True:
    time.sleep(1)
    pass

#fd