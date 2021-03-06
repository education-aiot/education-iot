import socket
import threading
import sqlite3
import sys
import time

PORT = 9040
BUF_SIZE = 1024
lock = threading.Lock()
clnt_data = []  # 접속한 클라이언트 정보 대입
clnt_cnt = 0  # 접속한 클라이언트 수
chat = 1      # 채팅방 번호
your_num = -1
my_num = -1
out = []

def conn_DB():
    conn = sqlite3.connect('edu.db')  # DB 연결
    cur = conn.cursor()
    return (conn, cur)


def handle_clnt(clnt_sock):
    for i in range(0, clnt_cnt):                    # 연결된 클라이언트가 몇 번째로 연결된 클라이언트인지 찾기
        if clnt_data[i][0] == clnt_sock:
            clnt_num = i
            break

    while 1:
        sys.stdout.flush()
        clnt_msg = clnt_sock.recv(BUF_SIZE)

        if not clnt_msg:
            print("client socket close")
            break

        clnt_msg = clnt_msg.decode()
        print("받은메세지 :" + clnt_msg)

        if clnt_msg.startswith('signup/'):
            clnt_msg = clnt_msg.replace('signup/', '')
            signup(clnt_num, clnt_msg)
        elif clnt_msg.startswith('login/'):
            clnt_msg = clnt_msg.replace('login/', '')
            login(clnt_num, clnt_msg)
        elif clnt_msg.startswith('logout/'):
            logout(clnt_num)
        elif your_num >= 0: 
            acceptance(clnt_num, clnt_msg)
        elif clnt_msg.startswith('chat/'):  ## 수정
            if clnt_data[clnt_num][2] != 0:  # 초기의 채팅방 상태는 0
                chatting(clnt_num, clnt_msg)
            #else:
            #    clnt_cnt.send('채팅상대를 초대하세요.'.encode()) ##수정
        elif clnt_msg.startswith('QnA/'):    # QnA 페이지
            qna(clnt_num)
        elif clnt_msg.startswith('Question/'):           # QnA 등록
            clnt_msg = clnt_msg.replace('Question/', '')
            qna_update(clnt_num, clnt_msg)
        elif clnt_msg.startswith('quiz/'):
            clnt_msg = clnt_msg.replace('quiz/', '')
            quiz_print(clnt_num, clnt_msg)
        elif clnt_msg.startswith('update/'):  # 문제 업데이트
            clnt_msg = clnt_msg.replace('update/', '')
            quiz_update(clnt_num, clnt_msg)
        elif clnt_msg.startswith('name_list/'): ## 수정 
            clnt_msg = clnt_msg.replace('name_list/', '') ## 수정 
            show_list(clnt_num)  # 학생이면 >> 선생님들 list 보냄 // 선생님이면 >> 학생 list 보냄
        elif clnt_msg.startswith('invite/'):  # invite/ name (초대)
            clnt_msg = clnt_msg.replace('invite/', '')
            invite(clnt_num, clnt_msg)
        elif clnt_msg.startswith('mark/'):
            clnt_msg = clnt_msg.replace('mark/', '')
            mark(clnt_num, clnt_msg)
        elif clnt_msg.startswith('avg/'):
            quiz_avg(clnt_num)
        elif clnt_msg.startswith('pw_change/'):
            clnt_msg = clnt_msg.replace('pw_change/', '')
            pw_change(clnt_num,clnt_msg)
        else:
            continue

        
def logout(clnt_num):
    global clnt_cnt
    global out
    clnt_sock = clnt_data[clnt_num][0]
    lock.acquire()
     # 로그아웃하는 클라이언트 소켓 fd 대입
    out = [clnt_data[clnt_num][0]]                 
    for i in range(0, clnt_cnt):          
        if clnt_sock == clnt_data[i][0]:             # 로그아웃하는 clnt_data 삭제
            while i < clnt_cnt - 1:
                clnt_data[i] = clnt_data[i + 1]
                i += 1
            if i == clnt_cnt-1:
                clnt_data.pop()
            break
    clnt_cnt -= 1
    lock.release()


def pw_change(clnt_num,clnt_msg):
    conn, cur=conn_DB()
    data = clnt_msg.split('/')
    # id/pw   확인 후 pw   update
    
    input_id=data[0]
    input_pw=data[1]

    member = clnt_data[clnt_num][1]
    clnt_sock = clnt_data[clnt_num][0]

    sql="select pw from  %s where id=?" %member
    cur.execute(sql,(input_id,)) # 실행
    pw=cur.fetchone() # 저장
    

    if not pw:
        clnt_sock.send('id error'.encode())
        return
     
    if (input_pw,) == pw: # pw
        clnt_sock.send('pw success'.encode())
    else :
        clnt_sock.send('pw mismatch'.encode())
        return
    

    new_pw=clnt_sock.recv(BUF_SIZE).decode()
    pw_update="update %s set pw =? where id=?" %member
    cur.execute(pw_update,(new_pw,input_id,))
    
    conn.commit()
    conn.close()



def mark(clnt_num, clnt_msg):
    conn, cur = conn_DB()
    check = clnt_msg.split('/')
    if check[1]  == 'o':
        check[1] = 100
    else:
        check[1] = 0
    lock.acquire()
    cur.executemany("INSERT INTO learning(num, score) VALUES (?, ?)", (check,))
    conn.commit()
    lock.release()
    conn.close()



def chatting(clnt_num, clnt_msg):
    print("채팅내용 : ", clnt_msg)
    for i in range(0, clnt_cnt):
        if clnt_data[i][2] == clnt_data[clnt_num][2]:  # 자신을 포함한 상대의 방번호가 같으면 
            if '그만하기' in clnt_msg and i != clnt_num: # clnt_msg에 그만하기 & 자기 자신이 아니면
                clnt_data[clnt_num][2] = 0 # 자기 자신은 채팅 여부는 0
                clnt_data[i][2] = 0
                clnt_data[i][0].send(('chat/' + clnt_data[clnt_num][5] + '님이 나갔습니다.').encode()) # 상대한테만 전송
                break
            clnt_data[i][0].send(clnt_msg.encode())  # 자신과 상대한테 for문 돌면서 전송



def invite(clnt_num, clnt_msg):
    global your_num
    global my_num
    clnt_sock = clnt_data[clnt_num][0] # my
    name = clnt_msg
    for i in range(0, clnt_cnt):
        if clnt_data[i][5] == name: #you_name
            clnt_data[i][0].send('채팅 초대'.encode())
            your_num = i
            my_num = clnt_num
            break


def acceptance(clnt_num, clnt_msg):
    global chat, my_num, your_num
    #채팅초대 받았을 때 답변 yes면
    if clnt_msg == 'yes': 
        clnt_data[my_num][0].send('수락'.encode())
        clnt_data[my_num][2] = chat
        clnt_data[your_num][2] = chat
        chat += 1
    else:
        clnt_data[my_num][0].send('거절'.encode())

    my_num = -1
    your_num = -1


def show_list(clnt_num):
    clnt_sock = clnt_data[clnt_num][0]
    member = clnt_data[clnt_num][1]
    all_name = []
    if member == 'student':
        all_name.append('TN')
        for i in range(0, clnt_cnt):
            if clnt_data[i][1] == 'teacher':
                all_name.append(clnt_data[i][5])
    elif member == 'teacher':
        all_name.append('SN')
        for i in range(0, clnt_cnt):
            if clnt_data[i][1] == 'student':
                all_name.append(clnt_data[i][5])

    all_name = '/'.join(all_name)
    clnt_sock.send(all_name.encode())


def qna(clnt_num):  # QnA 페이지 열면 QnA 목록 전송
    conn, cur = conn_DB()
    clnt_sock = clnt_data[clnt_num][0]

    cur.execute("SELECT * FROM QnA")  # DB에서 QnA 목록 조회
    rows = cur.fetchall()
    if not rows:                 # DB에 QnA 없으면
        clnt_sock.send("QnA/등록된 QnA 없음/ / ".encode())
    else:
        for row in rows:
            row = list(row)
            row[0] = str(row[0])
            for i in range(0, len(row)):     # None인 항목 찾기
                if row[i] is None:
                    row[i] = ' '             # None이면 공백으로
            row = '/'.join(row)              # / 로 나눠서 문자열 만들기

            row = "QnA/" + row
            print(row)
            clnt_sock.send(row.encode())
            time.sleep(0.1)
    conn.close()
# socket fd, member, chat, id, pw, nickname

def qna_update(clnt_num, clnt_msg):           # QnA 등록
    conn, cur = conn_DB()
    clnt_sock = clnt_data[clnt_num][0]
    member = clnt_data[clnt_num][1]
    name = clnt_data[clnt_num][5]

    if member == 'student':                    # 학생일 때 
        data = [name, clnt_msg]                # 닉네임, 질문
        lock.acquire()
        cur.executemany(
            "INSERT INTO QnA(studentname, question) VALUES(?, ?)", (data,))

    elif member == 'teacher':
        data = clnt_msg.split('/')
        data = [name] + data
        data[2] = int(data[2])
        lock.acquire()
        query = "UPDATE QnA SET teachername = '%s', answer = '%s' where num = %d" % (data[0], data[1], data[2])
        cur.execute(query)

    conn.commit()
    lock.release()
    conn.close()


def quiz_print(clnt_num, clnt_msg):
    conn, cur = conn_DB()
    clnt_sock = clnt_data[clnt_num][0]
    member = clnt_data[clnt_num][1]

    cur.execute("SELECT * FROM Quiz")
    rows = cur.fetchall()
    if not rows:
        print("퀴즈 없음")
        clnt_sock.send("등록된 quiz 없음".encode())

    else:
        for row in rows:
            row = list(row)
            row[0] = str(row[0])
            row = '/'.join(row)
            row = 'quiz/' + row
            clnt_sock.send(row.encode())
            print(row)
            time.sleep(0.1)

    conn.close()





def quiz_update(clnt_num, clnt_msg):
    conn, cur = conn_DB()

    member = clnt_data[clnt_num][1]
    lock.acquire()
    if member == 'teacher':
        data = clnt_msg.split('/')
        
        cur.executemany(
            "INSERT INTO Quiz(quiz, answer) VALUES (?, ?)", (data,))
        
    else:
        print("권한없음")

    conn.commit()
    lock.release()
    conn.close()


def quiz_avg(clnt_num):
    conn, cur = conn_DB()
    clnt_sock = clnt_data[clnt_num][0]
    cur.execute("SELECT num, AVG(score) FROM learning GROUP BY num")
    rows = cur.fetchall()
    if not rows:
        print("학습 데이터 없음")
        clnt_sock.send("학습데이터 없음".encode())
    else:
        for row in rows:
            row = list(row)
            row[1] = str(int(row[1]))
            row = '/'.join(row)
            row = 'avg/' + row
            print(row)
            clnt_sock.send(row.encode())
            time.sleep(0.1)
    clnt_sock.send("end_avg".encode())
    conn.close()


def signup(clnt_num, clnt_msg):
    conn, cur = conn_DB()
    user_data = []
    user_id = ''
    member = ''
    clnt_sock = clnt_data[clnt_num][0]

    while 1:
        overlap = False

        if clnt_msg.startswith('teacher/'):
            member = 'teacher'
            user_id = clnt_msg.replace('teacher/', '')
            print(user_id)
        elif clnt_msg.startswith('student/'):
            member = 'student'
            user_id = clnt_msg.replace('student/', '')
            print(user_id)
        else:
            print("error")
            conn.close()
            return

        query = "SELECT id FROM %s" % member
        rows = cur.execute(query)

        for row in rows:
            if user_id in row:
                # id 중복
                clnt_sock.send('NO'.encode())
                overlap = True
                break
        if overlap:
            print("id overlap")
            return

        clnt_sock.send('!OK'.encode())
        info = clnt_sock.recv(BUF_SIZE)
        info = info.decode()  # id/pw/name
        print("id/pw/name: ", info)

        info = info.split('/')

        for i in range(3):
            user_data.append(info[i])

        lock.acquire()
        insert_query = "INSERT INTO %s(id, pw, name) VALUES(?, ?, ?)" % member
        cur.executemany(insert_query, (user_data,))
        conn.commit()
        conn.close()
        lock.release()
        break


def login(clnt_num, clnt_msg):
    global clnt_cnt
    global out
    conn, cur = conn_DB() 
    member = ''
    #로그아웃 한 후에 다시 로그인할 때
    if out:                 
        lock.acquire()
        clnt_data.insert(clnt_cnt, out)
        clnt_cnt += 1 
        out = []
        lock.release()
    clnt_sock = clnt_data[clnt_num][0]   
    # login/member/id/pw
    if clnt_msg.startswith('teacher/'):                  
        member = 'teacher' 
        input_data = clnt_msg.replace('teacher/', '')   
    elif clnt_msg.startswith('student/'):
        member = 'student'
        input_data = clnt_msg.replace('student/', '')
        print(input_data)
    else:
        print("error")
        return

    input_data = input_data.split('/')
    input_id = input_data[0]
    input_pw = input_data[1]

    query = "SELECT pw FROM %s WHERE id =?" % member
    cur.execute(query, (input_id,))

    user_pw = cur.fetchone()

    if not user_pw:
        clnt_sock.send("id_error".encode())
        conn.close()
        return

    if (input_pw,) == user_pw:
        print("login sucess")
        clnt_data[clnt_num].append(member)
        clnt_sock.send("!OK".encode())
        query = "SELECT * FROM %s WHERE id = ?" % member
        cur.execute(query, (input_id,))
        user_data = cur.fetchone()
        user_data = list(user_data)
        clnt_data[clnt_num] = clnt_data[clnt_num] + [0] + user_data
        print("clnt_data:", clnt_data[clnt_num])
        # socket fd, member, chat, id, pw, nickname

    else:
        print("login fail")
        clnt_sock.send("pw_error".encode())
    conn.close()


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', PORT))
    sock.listen(5)

    while True:
        clnt_sock, addr = sock.accept()

        lock.acquire()
        clnt_data.insert(clnt_cnt, [clnt_sock])
        clnt_cnt += 1
        lock.release()
        thread = threading.Thread(target=handle_clnt, args=(clnt_sock,))
        thread.start()