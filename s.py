from socket import *
from threading import *
from queue import *
import sys
import datetime

#------------- 서버 세팅 -------------
HOST = '127.0.0.1' # 서버 ip 주소 .
PORT = 9190 # 사용할 포트 번호.
#------------------------------------

s=''
s+='\n  -------------< 사용 방법 >-------------'
s+='\n   연결 종료 : !quit 입력 or ctrl + c    '
s+='\n   참여 중인 멤버 보기 : !member 입력      '
s+='\n   귓속말 보내기 : /w [상대방이름] [메시지]   '
s+='\n -----------------------------------------'


def now_time():
    now = datetime.datetime.now()
    time_str=now.strftime('[%H:%M] ')
    return time_str

def send_func(lock): # 3)
    while True:
        try:
            msg=None # 최종전송 후 msg 들어 있는 거 초기화
            recv = received_msg_info.get()  ### 큐에 있는 거 순서대로 꺼냄
            # [data(== msg), clnt_sock, count] 순
            if recv[0]=='!quit' or len(recv[0])==0:  
                msg=str('[SYSTEM] '+now_time()+left_member_name)+'님이 연결을 종료하였습니다.'



            elif recv[0]=='!enter' or recv[0]=='!member':
                now_member_msg='현재 멤버 : '
                for mem in member_name_list:
                    if mem!='-1':
                        now_member_msg+='['+mem+'] '

                if(recv[0]=='!enter'):
                    msg=str('[SYSTEM] '+now_time()+member_name_list[recv[2]])+'님이 입장하였습니다.'

                else:
                    recv[1].send(now_member_msg.encode())




            elif recv[0].find('/w')==0: # 귓속말 기능
                split_msg=recv[0].split() # 귓속말 보내기 : /w [상대방이름] [메시지] 
                # queue >> [data(== msg), clnt_sock, count] 순
                if split_msg[1] in member_name_list: # [상대방이름] 검사
                    msg=now_time()+'(귓속말) '+member_name_list[recv[2]] +' : '
                    msg+=recv[0][len(split_msg[1])+4:len(recv[0])]
                    # 메세지 덪붙임         상대방이름 길이 +4,  data(==msg) 길이  ?????
                    idx=member_name_list.index(split_msg[1]) #상대방의 이름이 몇번째에 있는지 검사 후 배열 위치 반환
                    socket_list[idx].send(msg.encode()) # 해당 클라한테 전송
                else:
                    msg='해당 사용자가 존재하지 않습니다.'
                    recv[1].send(msg.encode())
                continue 


                
            else:
                msg = str(now_time() + member_name_list[recv[2]]) + ' : ' + str(recv[0])
                    #     시간         queue 꺼낸 리스트의 [2]에 count          [0]: msg


            for conn in socket_list: 
                if conn =='-1': # 연결 종료한 클라이언트 경우.
                    continue
                elif recv[1] != conn: #자신에게는 보내지 않음.
                    # queue >> [data(== msg), clnt_sock, count] 순
                    conn.send(msg.encode())   #  최종 전송
                else:
                    pass
            if recv[0] =='!quit':
                # queue >> [data(== msg), clnt_sock, count] 순
                recv[1].close()
        except:
            pass

def recv_func(clnt_sock, count, lock): # 201)

    if socket_list[count]=='-1': # 첫 번째 클라는 recv를 할 수 없다.
        return -1
    while True:
        global left_member_name
        data = clnt_sock.recv(1024).decode()
        received_msg_info.put([data, clnt_sock, count]) # data, clnt_sock, count에 큐 저장

        if data == '!quit' or len(data)==0:
            # len(data)==0 은 해당 클라이언트의 소켓 연결이 끊어진 경우에 대한 예외 처리임.
            lock.acquire() #  잠금
            print(str(now_time()+ member_name_list[count]) + '님이 연결을 종료하였습니다.')
            left_member_name=member_name_list[count] # 종료한 클라이언트 닉네임 저장.
            socket_list[count]= '-1'
            
            member_name_list[count]='-1'
            lock.release() # 잠금 해체
            break
    clnt_sock.close()


if __name__=="__main__":
    print(now_time()+'서버를 시작합니다')
    server_sock=socket(AF_INET, SOCK_STREAM)
    server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # Time-wait 에러 방지.
    server_sock.bind((HOST, PORT))
    server_sock.listen()

    count = 0
    socket_list=['-1',] # 클라이언트들의 소켓 디스크립터 저장.
    member_name_list=['-1',] # 클라이언트들의 닉네임 저장, 인덱스 접근 편의를 위해 0번째 요소 '-1'로 초기화.


    received_msg_info = Queue()
    left_member_name='' # 종료한 닉네임 저장
    lock=Lock()

    while True:
        count = count +1
        clnt_sock, addr = server_sock.accept()
        # clnt_sock과 addr에는 연결된 클라이언트의 정보가 저장된다.
        # clnt_sock : 연결된 소켓
        # addr[0] : 연결된 클라이언트의 ip 주소
        # addr[1] : 연결된 클라이언트의 port 번호

        while True:
            client_name=clnt_sock.recv(1024).decode() # 101) 이름 수신

            if not client_name in member_name_list:  # 1) 중복 없으면 yes 전송 >>>  (멈춤) 
                clnt_sock.send('yes'.encode())   # 102) 이름 전송
                break
            else:                                    # 1)      있으면 
                clnt_sock.send('overlapped'.encode()) 

        member_name_list.append(client_name)  ### 배열[1]부터 이름 추가
        socket_list.append(clnt_sock)         ### 배열[1]부터 소켓 추가
        
        print(str(now_time())+client_name+'님이 연결되었습니다. 연결 ip : '+ str(addr[0])) ### 101) 이름과 ip

        if count>1: 
            sender = Thread(target=send_func, args=(lock,))  # 202) 두 번째 클라부터 씀
            sender.start()
            pass
        else:
            sender=Thread(target=send_func, args=(lock,))    # 202) 첫 번째 클라가 씀
            sender.start()
        receiver=Thread(target=recv_func, args=(clnt_sock, count, lock)) # 201) 
        receiver.start()

#fdf