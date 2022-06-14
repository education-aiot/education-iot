import sqlite3
import sys
import time
from socket import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from threading import *
from random import *

ui = uic.loadUiType("base111.ui")[0]  # ui


class MainStudent(QWidget, ui):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 질문 row 세기
        self.qnacount = 0
        self.quizcount = 0
        self.scorecount = 0
        self.i = 0

        #학생 목록
        self.SN = []

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect(('127.0.0.1', 9040))

        # qna 테이블위젯 크기조정
        self.qna_table_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        #상담방 버튼
        self.quit_btn_2.clicked.connect(self.quitmessage)
        self.lineEdit_3.returnPressed.connect(self.sendconsul)


        #qna 버튼
        self.qna_renew_2.clicked.connect(self.renew)
        self.send_line_2.returnPressed.connect(self.sendqna)
        self.teach_back_btn3_2.clicked.connect(lambda: self.move_page('교사메인'))
        self.update_back_btn.clicked.connect(lambda: self.move_page('교사메인'))
        self.score_back_btn.clicked.connect(lambda: self.move_page('교사메인'))


        #로그인, 회원가입 버튼
        self.overlap_btn.clicked.connect(self.overlapCheck)
        self.login_btn.clicked.connect(self.Login)
        self.join_btn.clicked.connect(lambda: self.move_page('회원가입'))
        self.back_btn.clicked.connect(lambda: self.move_page('로그인'))

        # 교사용 에서 쓰는 버튼
        self.update_btn.clicked.connect(lambda : self.move_page('업데이트'))
        self.score_btn.clicked.connect(lambda: self.move_page('점수확인'))
        self.qna_btn_2.clicked.connect(lambda: self.move_page('QnA/'))
        self.consulting_btn_2.clicked.connect(self.consult)
        self.logout_btn.clicked.connect(lambda: self.move_page('로그아웃'))

        #문제 업데이트 버튼
        self.quiz_add_btn.clicked.connect(self.new_quiz)
        self.quiz_renew_btn.clicked.connect(self.update_renew)
        #학생 통계확인 버튼
        self.avg_btn.clicked.connect(self.score_renew)

    def receive_messages(self, sock):  # 메시지 받기
        global con
        while True:
            recv_message = sock.recv(4096)
            self.final_message = recv_message.decode('utf-8')
            print(self.final_message)

            # 서버에서 받을 문제,답
            if 'quiz/' in self.final_message:
                self.quiz = self.final_message.split('/')
                quiz_info = ['문제', '정답']
                self.update_table.setHorizontalHeaderLabels(quiz_info)
                try:
                    self.update_table.setRowCount((self.quizcount + 1))
                    self.update_table.setItem(self.quizcount, 0, QTableWidgetItem(self.quiz[2]))
                    self.update_table.setItem(self.quizcount, 1, QTableWidgetItem(self.quiz[3]))

                    self.quizcount += 1
                    globals()['lst{}'.format(self.i)] = [self.quiz[2], self.quiz[3]]
                    self.i += 1

                except:
                    pass


            elif 'QnA/' in self.final_message:

                self.qna = self.final_message.split('/')  # QnA/문제/답
                print(self.qna)
                columnname = ['번호', '질문', '답변', '학생이름', '선생님이름']
                self.qna_table_2.setHorizontalHeaderLabels(columnname)
                try:
                    self.qna_table_2.setRowCount((self.qnacount + 1))
                    self.qna_table_2.setItem(self.qnacount, 0, QTableWidgetItem(self.qna[1]))
                    self.qna_table_2.setItem(self.qnacount, 1, QTableWidgetItem(self.qna[2]))
                    self.qna_table_2.setItem(self.qnacount, 2, QTableWidgetItem(self.qna[3]))
                    self.qna_table_2.setItem(self.qnacount, 3, QTableWidgetItem(self.qna[4]))
                    self.qna_table_2.setItem(self.qnacount, 4, QTableWidgetItem(self.qna[5]))
                    self.qnacount += 1

                    globals()['lst{}'.format(self.i)] = [self.qna[1], self.qna[2], self.qna[3], self.qna[4], self.qna[5]]
                    self.i += 1
                except:
                    pass

            elif 'avg/' in self.final_message:
                self.avg = self.final_message.split('/')
                avg_info = ['문제번호', '정답률']
                self.score_screen.setHorizontalHeaderLabels(avg_info)
                try:
                    self.score_screen.setRowCount((self.scorecount +1))
                    self.score_screen.setItem(self.scorecount, 0, QTableWidgetItem(self.avg[1]))
                    self.score_screen.setItem(self.scorecount, 1, QTableWidgetItem(self.avg[2]))

                    self.scorecount += 1
                    globals()['lst{}'.format(self.i)] = [self.avg[1], self.avg[2]]
                    self.i += 1

                except:
                    pass

            elif '채팅 초대' in self.final_message:
                # QmessageBox로 yes or no 판별
                invite=QMessageBox.question(self,"초대요청", "상담방에 초대받으셨습니다. ",QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)

                if invite==QMessageBox.Yes:
                    self.sock.send('yes'.encode())
                    self.move_page('상담방')

                else:
                    self.sock.send('수락 거절'.encode())

            elif 'chat/' in self.final_message:
                name = self.final_message.split('/')[-2]
                chat = self.final_message.split('/')[-1]
                self.textBrowser_2.append(name + ':' + chat)
                pass
            elif 'SN/' in self.final_message:
                try:
                    self.student = self.final_message.split('/')
                except:
                    pass
                print(self.student)

    #문제 불러오기

    #상담방 그만하기 버튼
    def quitmessage(self):
        self.sock.send('chat/그만하기'.encode())
        self.move_page('교사메인')

    # 답변 보내기
    def sendqna(self):
        sendData = f'Question/{self.send_line_2.text()}'# 답변/질문번호 로 보내기
        self.sock.send(sendData.encode('utf-8'))
        self.send_line_2.clear()

    def consult(self): #상담요청 버튼
        self.sock.send('name_list/'.encode())
        time.sleep(0.3)
        for i in range(len(self.student)):
            try:
                self.SN.append(self.student[i + 1])
            except:
                pass

        item, ok = QInputDialog.getItem(self, "학생 목록", "학생을 선택하세요.", self.SN, 0, False)
        if ok and item:
            print('학생이름:',item)
            self.sock.send(f'invite/{item}'.encode())

        # if '수락' in self.final_message:
            self.move_page('상담방')
            self.SN.clear()


    def sendconsul(self): # 상담 메지시 보내기
        sendDataa = f'chat/{self.login_id}/{self.lineEdit_3.text()}'

        self.sock.send(sendDataa.encode('utf-8'))
        self.lineEdit_3.clear()

    # def sendconsul(self):
    #     sendData = f'chat/{self.login_id}/{self.lineEdit.text()}'
    #     self.sock.send(sendData.encode('utf-8'))
    #     self.lineEdit.clear()
    #
    # def invitemessage(self):
    #     sendData = f'invite/'
    #     self.sock.send('invite/'.encode('utf-8'))
    #
    # def invitemess(self):
    #     sendData = f'chat/{self.lineEdit.text()}'
    #     self.sock.send(sendData.encode('utf-8'))
    #     self.move_page('상담방')

    def renew(self):  # 질문 페이지 새로고침
        self.qnacount = 0
        self.sock.send('QnA/'.encode())
        columnname = ['번호', '질문', '답변', '학생이름', '선생님이름']
        self.qna_table_2.setHorizontalHeaderLabels(columnname)
        self.qna_table_2.setRowCount((self.qnacount + 1))

        for i in range(self.i):
            print(self.i)

            self.qna_table_2.setItem(i, 0, QTableWidgetItem(globals()['lst{}'.format(i)][0]))
            self.qna_table_2.setItem(i, 1, QTableWidgetItem(globals()['lst{}'.format(i)][1]))
            self.qna_table_2.setItem(i, 2, QTableWidgetItem(globals()['lst{}'.format(i)][2]))
            self.qna_table_2.setItem(i, 3, QTableWidgetItem(globals()['lst{}'.format(i)][3]))
            self.qna_table_2.setItem(i, 4, QTableWidgetItem(globals()['lst{}'.format(i)][4]))
            print('i:', i)

        self.i=0
        self.qna_table_2.clear()

    def update_renew(self):
        self.quizcount = 0
        self.sock.send('quiz/'.encode())
        quiz_info = ['문제','정답']
        self.update_table.setHorizontalHeaderLabels(quiz_info)
        self.update_table.setRowCount((self.quizcount + 1))

        for i in range(self.i):
            print(self.i)

            self.update_table.setItem(i, 0, QTableWidgetItem(globals()['lst{}'.format(i)][0]))
            self.update_table.setItem(i, 1, QTableWidgetItem(globals()['lst{}'.format(i)][1]))
            print('i:', i)

        self.i = 0
        self.update_table.clear()

    def score_renew(self):
        self.scorecount = 0
        self.sock.send('avg/'.encode())
        avg_info = ['문제번호','정답률']
        self.score_screen.setHorizontalHeaderLabels(avg_info)
        self.score_screen.setRowCount((self.scorecount + 1))

        for i in range(self.i):
            print(self.i)

            self.score_screen.setItem(i, 0, QTableWidgetItem(globals()['lst{}'.format(i)][0]))
            self.score_screen.setItem(i, 1, QTableWidgetItem(globals()['lst{}'.format(i)][1]))
            print('i:', i)

        self.i = 0
        self.score_screen.clear()



    # 중복확인
    def overlapCheck(self):
        self.sign_id = self.join_id_edit.text()  # 회원가입 ID lineEdit 값 가져오기
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

    # 로그인 했을 때
    def Login(self):
        self.login_id = self.login_id_edit.text()  # 로그인 ID lineEdit 값 가져오기
        self.login_pw = self.login_pw_edit.text()  # 로그인 PW lineEdit 값 가져오기
        self.sock.send(f"{'login/' + 'teacher/' + self.login_id + '/' + self.login_pw}".encode())  # 로그인/ID/PW
        print('아이디:', self.login_id)

        recv_message = self.sock.recv(4096).decode()
        print('로그인 메시지: ', recv_message)
        if '!OK' in recv_message:
            self.move_page('교사메인')

        elif 'id_error' in recv_message:
            QMessageBox.information(self, '로그인', '아이디 또는 비밀번호가\n잘못 되었습니다.')

        else:
            pass

    # 교사구별?
    def SignUp(self):
        QMessageBox.information(self, '회원가입', '회원가입 성공!.')
        self.sign_pw = self.join_pw_edit.text()
        self.nickname = self.join_name_edit.text()
        self.move_page('로그인')
        self.sock.send(f'{self.sign_id}/{self.sign_pw}/{self.nickname}'.encode('utf-8'))
        print('')

    def move_page(self, page):
        if page == '로그인':
            self.stackedWidget_2.setCurrentWidget(self.login_page_2)
        elif page == '회원가입':
            self.stackedWidget_2.setCurrentWidget(self.register_page_2)
        elif page == '로그아웃':
            self.stackedWidget_2.setCurrentWidget(self.login_page_2)
            self.sock.send(f"{'logout/' + 'teacher/' + self.login_id + '/' + self.login_pw}".encode())

        # qna 부분 버튼
        elif page == 'QnA/':
            self.stackedWidget_2.setCurrentWidget(self.teach_qna_page)
            self.sock.send('QnA/'.encode())
            # self.qna_table_2.setRowCount(0)
            self.qnacount = 0
            self.qna_table_2.clear()

        elif page == '교사메인':
            self.stackedWidget_2.setCurrentWidget(self.teacher_main_page)
            receiver = Thread(target=self.receive_messages, args=(self.sock,))  # 수신 스레드
            receiver.start()

        # 교사용 위젯 버튼
        elif page == '업데이트':
            self.stackedWidget_2.setCurrentWidget(self.update_page)

        #점수 확인 하고 싶은 학생 점수 요청?
        elif page == '점수확인':
            self.stackedWidget_2.setCurrentWidget(self.score_page)

        elif page == '상담방':
            self.stackedWidget_2.setCurrentWidget(self.consulting_page_2)

    # 문제 업데이트
    def new_quiz(self):
        self.newquiz = self.newquiz_edit.text()
        self.newanswer = self.newanswer_edit.text()
        self.sock.send(f"{'update/' + self.newquiz + '/' + self.newanswer}".encode('utf-8'))
        self.newquiz_edit.clear()
        self.newanswer_edit.clear()


if __name__ == '__main__':
    # Data()

    app = QApplication(sys.argv)
    ex = MainStudent()
    ex.show()
    app.exec()
