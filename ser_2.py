import socket
import threading
import sqlite3
import sys

PORT = 9040
BUF_SIZE = 1024
lock = threading.Lock()
clnt_data = []  # 접속한 클라이언트 정보 대입
clnt_cnt = 0  # 접속한 클라이언트 수
chat = 1 # 채팅방번호 부여


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
        print(clnt_msg)

        if clnt_msg.startswith('signup/'):
            clnt_msg = clnt_msg.replace('signup/', '')
            print(clnt_msg)
            signup(clnt_num, clnt_msg)
        elif clnt_msg.startswith('login/'):
            clnt_msg = clnt_msg.replace('login/', '')
            print(clnt_msg)
            login(clnt_num, clnt_msg)
        elif clnt_msg.startswith('chat/'):  ## 수정
            if clnt_data[clnt_num][2] != 0:  # 초기의 채팅방 상태는 0
                chatting(clnt_num, clnt_msg)
            else:
                clnt_cnt.send('채팅상대를 초대하세요.'.encode()) ##수정
        elif clnt_msg.startswith('QnA/'):    # QnA 페이지
            qna(clnt_num)
        elif clnt_msg.startswith('QnA_upload/'):           # QnA 등록
            clnt_msg = clnt_msg.replace('QnA_upload/','')
            qna_update(clnt_num, clnt_msg)
        elif clnt_msg.startswith('quiz/'):
            clnt_msg = clnt_msg.replace('quiz/', '')
            quiz_print(clnt_num, clnt_msg)
        elif clnt_msg.startswith('name_list/'): ## 수정 
            clnt_msg = clnt_msg.replace('name_list/', '') ## 수정 
            show_list(clnt_num)  # 학생이면 >> 선생님들 list 보냄 // 선생님이면 >> 학생 list 보냄
        elif clnt_msg.startswith('invite/'):  # 초대     invite/ name
            clnt_msg = clnt_msg.replace('invite/', '')  # invite   >>  공백
            invite(clnt_num, clnt_msg)
        else:
            continue

# 채팅방에서 '그만하기' >> 채팅방 상태를 모두 0 >> 채팅 끊기

    
def chatting(clnt_num, clnt_msg):
    for i in range(0, clnt_cnt):
        if clnt_data[i][2] == clnt_data[clnt_num][2]:  # 자신을 포함한 상대의 방번호가 같으면 
            if '그만하기' in clnt_msg and i != clnt_num: # clnt_msg에 그만하기 & 자기 자신이 아니면
                clnt_data[clnt_num][2] = 0 # 자기 자신은 채팅 여부는 0
                clnt_data[i][0].send(clnt_data[clnt_num][5]+'나갔습니다.'.encode()) # 상대한테만 전송
                break
            clnt_data[i][0].send(clnt_msg.encode())  # 자신과 상대한테 for문 돌면서 전송 
            

def invite(clnt_num, clnt_msg):
    clnt_sock = clnt_data[clnt_num][0]  # 본인 소켓
    name = clnt_msg  # 이름으로 바꿈
    for i in range(0, clnt_cnt):
        if clnt_data[i][5] == name:  # 초대한 사람 찾기
            clnt_data[i][0].send('채팅 초대'.encode())  # 상대 소켓에게 "채팅 초대" 보냄
            break

    recv_msg = clnt_data[i][0].recv(BUF_SIZE)  # 상대 클라의 메세지 올 때 까지 대기
    recv_msg = recv_msg.decode()
    if recv_msg == 'yes':
        clnt_sock.send('수락'.encode())
        clnt_data[i][2] = chat  # 상대 채팅방 번호 부여
        clnt_data[clnt_num][2] = chat  # 본인 채팅방 번호 부여
        chat += 1
    else:
        clnt_sock.send('거절'.encode())


def show_list(clnt_num):
    clnt_sock = clnt_data[clnt_num][0]  # 본인의 소켓
    member = clnt_data[clnt_num][1]  # 본인 등급
    all_name = []
    if member == 'student':  # 본인 등급이 학생이면
        for i in range(0, clnt_cnt):
            if clnt_data[i][1] == 'teacher':
                # clnt_data[i][4] 이름이 담겨있음  >> 모든 선생님의 이름이 담김
                all_name.append(clnt_data[i][4])
    elif member == 'teacher':  # 본인 등급이 선생님이면
        for i in range(0, clnt_cnt):
            if clnt_data[i][1] == 'teacher':
                all_name.append(clnt_data[i][4])

    all_name = '/'.join(all_name)  # [a,b,c,d,e] >> [a/b/c/d/e] 변형
    clnt_sock.send(all_name)  # 해당 소켓에게 보냄


def qna(clnt_num):  # QnA 페이지 열면 QnA 목록 전송
    conn, cur = conn_DB()
    clnt_sock = clnt_data[clnt_num][0]

    cur.execute("SELECT * FROM QnA")  # DB에서 QnA 목록 조회
    rows = cur.fetchall()
    if not rows:                 # DB에 QnA 없으면
        clnt_sock.send("QnA/등록된 QnA 없음".encode())
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
    conn.close()


def qna_update(clnt_num, clnt_msg):           # QnA 등록
    conn, cur = conn_DB()
    clnt_sock = clnt_data[clnt_num][0]
    member = clnt_data[clnt_num][1]
    name = clnt_data[clnt_num][5]

    if member == 'student':                    # 학생이면
        data = clnt_msg.split('/')             # 학생이름, 질문
        lock.acquire()
        cur.executemany(
            "INSERT INTO QnA(studentname, question) VALUES(?, ?)", (data,))

    elif member == 'teacher':
        data = clnt_msg.split('/')
        lock.acquire()
        cur.execute(
            "UPDATE QnA SET teachername = ?, answer = ? WHERE num = ?,", (data,))

    conn.commit()
    lock.release()
    conn.close()


def quiz_print(clnt_num, clnt_msg):
    conn, cur = conn_DB()
    clnt_sock = clnt_data[clnt_num][0]
    member = clnt_data[clnt_num][1]

    if member == 'student':
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
                print(row)
                clnt_sock.send(row.encode())

    else:
        print("권한없음")

    conn.close()


def quiz_result(clnt_num, clnt_msg):
    conn, cur = conn_DB()
    id = clnt_data[clnt_num][3]
    save = clnt_data[clnt_num][6]
    point = int(clnt_data[clnt_num][7])

    data = clnt_msg.split('/')
    data.insert(-1, id)
    cur.execute("UPDATE student SET save = ?, point = ? WHERE id = ?", (data,))


def quiz_update(clnt_num, clnt_msg):
    conn, cur = conn_DB()

    member = clnt_data[clnt_num][1]
    if member == 'teacher':
        data = clnt_msg.split('/') # 큐즈/답    ( 구문자마다 '/' 넣음) 
        lock.acquire()
        cur.executemany(
            "INSERT INTO Quiz(quiz, answer) VALUES (?, ?)", (data,))
    else:
        print("권한없음")

    conn.commit()
    lock.release()
    conn.close()


def quiz_avg(clnt_num, clnt_msg):
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
            row[0] = str(row[0])
            row = '/'.join(row)
            print(row)
            clnt_sock.send(row.encode())

    conn.close()


def signup(clnt_num, clnt_msg):
    conn, cur = conn_DB()
    user_data = []
    user_id = ''
    member = ''
    clnt_sock = clnt_data[clnt_num][0]

    while 1:
        overlap = False

        if clnt_msg == "close":
            conn.close()
            return

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
        if info == 'close':
            conn.close()
            break

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
    conn, cur = conn_DB()
    member = ''
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

        print("clnt_data:", clnt_data[clnt_num])
        clnt_sock.send("!OK".encode())
        query = "SELECT * FROM %s WHERE id = ?" % member
        cur.execute(query, (input_id,))
        user_data = cur.fetchone()
        user_data = list(user_data)
        print("user_data ", user_data)
        clnt_data[clnt_num] = clnt_data[clnt_num] + [0] + user_data
        print("clnt_data:", clnt_data[clnt_num])

        '''확인용
        member = clnt_data[clnt_num][1]
        name = clnt_data[clnt_num][5]
        print("member", member, "name", name) 
        '''

    else:
        print("login fail")
        clnt_sock.send("pw_error".encode())
    conn.close()


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', PORT))
    sock.listen(5)

    while True:
        clnt_sock, addr = sock.accept()

        lock.acquire()
        clnt_data.insert(clnt_cnt, [clnt_sock])
        print("clnt_data", clnt_data)
        clnt_cnt += 1
        lock.release()
        thread = threading.Thread(target=handle_clnt, args=(clnt_sock,))
        thread.start()
