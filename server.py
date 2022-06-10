import socket
import threading
import sqlite3
import sys


PORT = 9041
BUF_SIZE = 1024
lock = threading.Lock()
clnt_data = []
clnt_cnt = 0



def conn_DB():
    conn = sqlite3.connect('edu.db') # DB 연결
    cur = conn.cursor()
    return (conn, cur)


def handle_clnt(clnt_sock):
    for i in range(0, clnt_cnt):
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
        elif clnt_msg.startswith('QnA/'):
            qna(clnt_num)
        elif clnt_msg.startswith('quiz/'):
            clnt_msg = clnt_msg.replace('quiz/', '')
            quiz(clnt_num, clnt_msg)
        elif clnt_msg.startswith('chat/'):
            clnt_msg = clnt_msg.replace('chat/', '')
        elif clnt_msg.startswith('qna_upload/'):           # QnA 등록
            clnt_msg = clnt_msg.replace('qna_upload/,' '')
            qna_update(clnt_num, clnt_msg)


def qna(clnt_num): # QnA 
    conn, cur = conn_DB()
    clnt_sock = clnt_data[clnt_num][0]

    cur.execute("SELECT * FROM QnA")
    rows = cur.fetchall()
    if not rows:
        clnt_sock.send("등록된 QnA 없음".encode())
        return
    else:
        for row in rows:
            row = list(row)
            row[0] = str(row[0])
            for i in range(0, len(row)):     # None인 항목 찾기
                if row[i] is None:
                    row[i] = ' '
            row = '/'.join(row)

            print(row)
            clnt_sock.send(row.encode())
    conn.close()


def qna_update(clnt_num, clnt_msg):
    conn, cur = conn_DB()
    clnt_sock = clnt_data[clnt_num][0]
    member = clnt_data[clnt_num][1]
    name = clnt_data[clnt_num][4]
    
    if member == 'student':
        data = [name, clnt_msg]
        cur.executemany("INSERT INTO QnA(studentname, question) VALUES(?, ?)", (data,))
        
    elif member == 'teacher':
        data = clnt_msg.split('/') # answer, num
        data.insert(0, name)
        cur.execute("UPDATE QnA SET teachername = ?, answer = ? WHERE num = ?,", (data,))

    conn.commit()
    conn.close()


def quiz(clnt_num, clnt_msg):
    conn, cur = conn_DB()
    member = clnt_data[clnt_num][1]
    id = clnt_data[clnt_num][2]

    if member == 'student':
        cur.execute("SELECT * FROM Quiz")
        rows = cur.fetchall()
        if not rows:
            print("퀴즈 없음")
            clnt_sock.send("등록된 quiz 없음".encode())
            return
        for row in rows:
            row = list(row) 
            row[0] = str(row[0])
            row = '/'.join(row)
            print(row)
            clnt_sock.send(row.encode())
    else:
        print("권한없음")


def quiz_update(clnt_num, clnt_msg):
    conn, cur = conn_DB()
    member = clnt_data[clnt_num][1]
    if member == 'teacher':
        data = clnt_msg.split('/')
        cur.executemany("INSERT INTO Quiz(quiz, answer) VALUES (?, ?)", (data,))
    else:
        print("권한없음")

    conn.commit()
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
        info = info.decode() # id/pw/name 
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
    member=''
    clnt_sock = clnt_data[clnt_num][0]
    #login/member/id/pw
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
        clnt_data[clnt_num] = clnt_data[clnt_num] + user_data
        print("clnt_data:", clnt_data[clnt_num])

        '''확인용
        member = clnt_data[clnt_num][1]
        name = clnt_data[clnt_num][4]
        print("member", member, "name", name) 
        '''
        
    else :
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
        thread = threading.Thread(target = handle_clnt, args = (clnt_sock,))
        thread.start()