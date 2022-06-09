import sqlite3
import sys
from socket import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from threading import *
from random import *

datacon = sqlite3.connect('Animal.db')
ui = uic.loadUiType("base.ui")[0]


class MainStudent(QWidget, ui):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.con = sqlite3.connect("Animal.db")
        self.dic = {}
        self.num = []
        self.score = 0
        self.nickname=self.join_name_edit.text()
        self.count = 0  # 문제 갯수 세기용
        # self.lcdNumber.display(self.score)
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect(('127.0.0.1', 9040))



        self.send_line.returnPressed.connect(self.sendqna)
        self.overlap_btn.clicked.connect(self.overlapCheck)
        self.login_btn.clicked.connect(self.Login)
        self.qna_btn.clicked.connect(lambda: self.move_page('QnA'))
        self.study_btn.clicked.connect(lambda: self.move_page('학생학습자료'))
        self.stu_back_btn.clicked.connect(lambda: self.move_page('학생메인'))
        self.stu_back_btn2.clicked.connect(lambda: self.move_page('학생메인'))
        self.stu_back_btn3.clicked.connect(lambda: self.move_page('학생메인'))
        self.solv_btn.clicked.connect(self.solv_page)
        self.back_btn.clicked.connect(lambda: self.move_page('로그인'))
        self.join_btn.clicked.connect(lambda: self.move_page('회원가입'))
        self.randchoice_btn.clicked.connect(self.uploadques)
        # self.randchoice_btn.clicked.connect(lambda :self.sol())

    def receive_messages(self, sock):
        while True:
            recv_message = sock.recv(4096)
            self.final_message = recv_message.decode('utf-8')
            print('QnA 받은메시지: ', self.final_message)
            if 'question/' in self.final_message:
                recvmess=self.final_message.split('question/')
                with self.con:
                    cur = self.con.cursor()
                    cur.execute(f'insert into 문제집 values ({recvmess[1]})')
            elif 'QnA/' in self.final_message:
                pass
            self.textBrowser.append(self.final_message)

    def sendqna(self):  # QnA or 상담용 채팅방?
        if self.send_line.text() == '':
            pass
        else:
            self.nickname = self.join_name_edit.text()
            if self.nickname == '':
                self.nickname = '익명'
            sendData = f'QnA/student/{self.nickname}:{self.send_line.text()}'  # QnA/student/닉네임:내용
            self.sock.send(sendData.encode('utf-8'))
            self.send_line.clear()

    def overlapCheck(self):
        self.sign_id = self.join_id_edit.text()  # 회원가입 ID lineEdit 값 가져오기
        self.sign_pw = self.join_pw_edit.text()  # 회원가입 PW lineEdit 값 가져오기
        print(self.join_cb_2.currentText())
        if self.join_cb_2.currentText() == '학생':  # 체크박스 여부에 따라 전송데이터 판단
            sendData = f"{'signup/student/' + self.sign_id}"
        else:
            sendData = f"{'signup/teacher/' + self.sign_id}"

        self.sock.send(sendData.encode())  # 회원가입/ID/PW

        recv_message = self.sock.recv(4096).decode()
        print('회원가입 메시지: ', recv_message)

        if '!OK' in recv_message:
            QMessageBox.information(self, '중복확인', '사용가능한 아이디입니다.')
            self.back_btn.clicked.connect(self.SignUp)  # 통과시 회원가입 성공 메시지 or 로그인페이지 이동

        else:
            QMessageBox.warning(self, '중복확인', '이미 존재하는 아이디입니다.')

    def Login(self):
        login_id = self.login_id_edit.text()  # 로그인 ID lineEdit 값 가져오기
        login_pw = self.login_pw_edit.text()  # 로그인 PW lineEdit 값 가져오기
        self.sock.send(f"{'login/' +'student/'+ login_id + '/' + login_pw}".encode())  # 로그인/ID/PW

        recv_message = self.sock.recv(4096).decode()
        print('로그인 메시지: ', recv_message)
        if '!OK' in recv_message:
            self.move_page('학생메인')
        else:
            pass

    def SignUp(self):
        QMessageBox.information(self, '회원가입', '회원가입 성공!.')
        self.sign_pw = self.join_pw_edit.text()
        self.nickname = self.join_name_edit.text()
        self.move_page('로그인')
        self.sock.send(f'{self.sign_id}/{self.sign_pw}/{self.nickname}'.encode('utf-8'))

    def move_page(self, page):
        if page == '로그인':
            self.stackedWidget_2.setCurrentWidget(self.login_page_2)
        elif page == 'QnA':
            self.stackedWidget_2.setCurrentWidget(self.qna_page_2)
            receiver = Thread(target=self.receive_messages, args=(self.sock,))  # 수신 스레드
            receiver.start()
        elif page == '학생메인':
            self.stackedWidget_2.setCurrentWidget(self.student_main_page)
        elif page == '학생학습자료':
            self.stackedWidget_2.setCurrentWidget(self.student_page1)
            i = 0

            with self.con:
                cur = self.con.cursor()
                rows = cur.execute('select 출현종수,출현종,식생유형,토지유형,자치구명,조사지역,조사연도,종수범례 from 출현현황')

                for row in rows:
                    self.tableWidget.setRowCount((i + 1))
                    changetype = list(row)
                    for j in range(8):
                        self.tableWidget.setItem(i, j, QTableWidgetItem(str(changetype[j])))
                    i += 1
        elif page == '문제풀기':
            self.stackedWidget_2.setCurrentWidget(self.student_quiz)
        elif page == '회원가입':
            self.stackedWidget_2.setCurrentWidget(self.register_page_2)

    def sol(self, num):
        return f'select 문제 from 문제집 where 답={num}'

    def solv_page(self):
        with self.con:
            cur = self.con.cursor()
            rows = cur.execute('select * from 문제집')
            for row in rows:
                self.count += 1
                self.dic[row[0]] = row[1]  # 문제,답 딕셔너리 만들기
                self.sock.send(f"question/{row[0]}/{row[1]}".encode())  # questione/(문제1,1)
        self.move_page('문제풀기')

    def uploadques(self):
        i=0
        with self.con:
            cur = self.con.cursor()
            rows = cur.execute(f'select * from 문제집')

            for row in rows:
                self.tableWidget_2.setRowCount((i + 1))
                upload = list(row)
                print(upload)
                for j in range(2):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(upload[j]))
                i += 1





    def memo(self):
        self.dialog = QDialog()
        self.dialog.setWindowTitle('메모장')
        self.dialog.resize(400, 400)
        self.dialog.show()
        # self.sock.send(f"question/{}".encode())


if __name__ == '__main__':
    # Data()

    app = QApplication(sys.argv)
    ex = MainStudent()
    ex.show()
    app.exec()