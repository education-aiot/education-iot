import sqlite3
import sys
from socket import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from threading import *
from random import *
import time

ui = uic.loadUiType("base111.ui")[0] # ui
con=sqlite3.connect("Animal.db")
class MainStudent(QWidget, ui):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.con = sqlite3.connect("Animal.db", check_same_thread=False)# db연결
        self.dic = {} # 문제:답 딕셔너리 06/10 사용 x 혹시나 몰라서 놔둠.
        self.num = [] #

        self.answer_lst=[] # 답 리스트
        self.wrong_answer=[] # 틀린답 리스트
        self.i=0

        self.count = 0  # 문제 갯수 세기용
        self.qnacount=0 # 질문 row 세기
        self.rowcounts=0
        self.sock = socket(AF_INET, SOCK_STREAM) #소켓
        self.sock.connect(('127.0.0.1', 9040)) # 소켓연결
        self.pw_change_dialog = QDialog()
        self.tableWidget_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)# 테이블위젯 크기조정
        self.qna_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)# 테이블위젯 크기조정
        # 버튼 클릭
        self.consulting_btn.clicked.connect(self.consult)
        self.quit_btn.clicked.connect(self.quitmessage) # 나가기버튼
        self.save_btn.clicked.connect(self.save) #저장버튼
        self.load_btn.clicked.connect(self.load) # 불러오기버튼
        self.qna_renew.clicked.connect(self.renew) # 새로고침버튼
        self.send_line.returnPressed.connect(self.sendqna)
        self.lineEdit.returnPressed.connect(self.sendconsul)
        self.overlap_btn.clicked.connect(self.overlapCheck)
        self.check_ans_btn.clicked.connect(self.check_answer)
        self.login_btn.clicked.connect(self.Login)
        self.qna_btn.clicked.connect(lambda: self.move_page('QnA/'))
        self.study_btn.clicked.connect(lambda: self.move_page('학생학습자료'))
        self.stu_back_btn.clicked.connect(lambda: self.move_page('학생메인'))
        self.stu_back_btn2.clicked.connect(lambda: self.move_page('학생메인'))
        self.stu_back_btn3.clicked.connect(lambda: self.move_page('학생메인'))
        self.solv_btn.clicked.connect(self.solv_page)
        self.back_btn.clicked.connect(lambda: self.move_page('로그인'))
        self.join_btn.clicked.connect(lambda: self.move_page('회원가입'))
        self.randchoice_btn.clicked.connect(self.uploadques)
        self.pwchangebtn.clicked.connect(self.pw_change)




        stumain = QPixmap()
        stumain.load('/home/ai2022/PycharmProjects/1_project/png/stu_main.png')
        self.stumain.setPixmap(stumain)

        stuqna = QPixmap()
        stuqna.load('/home/ai2022/PycharmProjects/1_project/png/stu_QnA.png')
        self.stuqna.setPixmap(stuqna)

        # teaqna = QPixmap()
        # teaqna.load('/home/ai2022/PycharmProjects/1_project/png/stu_QnA.png')
        # self.teaqna.setPixmap(teaqna)

        stuconsult = QPixmap()
        stuconsult.load('/home/ai2022/PycharmProjects/1_project/png/stu_consult.png')
        self.stuconsult.setPixmap(stuconsult)

        stulearn = QPixmap()
        stulearn.load('/home/ai2022/PycharmProjects/1_project/png/stu_learn.png')
        self.stulearn.setPixmap(stulearn)

        stusol = QPixmap()
        stusol.load('/home/ai2022/PycharmProjects/1_project/png/stu_quiz.png')
        self.stusol.setPixmap(stusol)

        stumainbtn = QPixmap()
        stumainbtn.load('/home/ai2022/PycharmProjects/1_project/png/1.png')
        self.stumainbtn.setPixmap(stumainbtn)

        stumainbtn2 = QPixmap()
        stumainbtn2.load('/home/ai2022/PycharmProjects/1_project/png/1.png')
        self.stumainbtn2.setPixmap(stumainbtn2)


    def insql(self,query): #쿼리문 작성용
        with self.con:
            cur = self.con.cursor()
            cur.execute(query)

    def receive_messages(self, sock): # 메시지 받기
        global con
        while True:
            recv_message = sock.recv(4096)
            self.final_message = recv_message.decode('utf-8')

            print(self.final_message)


            if 'quiz/' in self.final_message:
                self.rowcounts+=1
                quiz=self.final_message.split('/')

                print(f'insert into 문제집 values ("{quiz[2]}","{quiz[3]}")')
                self.answer_lst.append(quiz[3])
                try:
                    with self.con:
                        cur=self.con.cursor()
                        cur.execute(f'insert into 문제집 values ("{quiz[2]}","{quiz[3]}")')
                except:
                    pass
                self.tableWidget_2.setRowCount((self.rowcounts))
                self.tableWidget_2.setItem(self.rowcounts-1, 0, QTableWidgetItem(quiz[2]))
                print(self.rowcounts)
                print('퀴즈:', quiz[2])





            elif 'QnA/' in self.final_message:

                self.qna=self.final_message.split('/') # QnA/문제/답
                print(self.qna)
                columnname = ['번호', '질문', '답변', '학생이름', '선생님이름']
                self.qna_table.setHorizontalHeaderLabels(columnname) # 컬럼 이름 설정
                try:
                    self.qna_table.setRowCount((self.qnacount+1)) # 테이블 위젯 row갯수
                    self.qna_table.setItem(self.qnacount, 0, QTableWidgetItem(self.qna[1]))
                    self.qna_table.setItem(self.qnacount, 1, QTableWidgetItem(self.qna[2]))
                    self.qna_table.setItem(self.qnacount, 2, QTableWidgetItem(self.qna[3]))
                    self.qna_table.setItem(self.qnacount, 3, QTableWidgetItem(self.qna[4]))
                    self.qna_table.setItem(self.qnacount, 4, QTableWidgetItem(self.qna[5]))
                    self.qnacount += 1

                    globals()['lst{}'.format(self.i)] = [self.qna[1], self.qna[2], self.qna[3], self.qna[4], self.qna[5]]
                    # 변수 lst0,lst1 ... 생성하기
                    self.i+=1
                except:
                    pass

            elif '채팅 초대' in self.final_message:

                # QmessageBox로 yes or no 판별
                invite=QMessageBox.question(self,"초대요청", "상당방에 초대받으셨습니다. ",QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)

                if invite==QMessageBox.Yes:
                    self.sock.send('yes'.encode())
                    self.move_page('상담방')

                else:
                    self.sock.send('수락 거절'.encode())

            elif 'chat/' in self.final_message:
                name = self.final_message.split('/')[-2]
                chat = self.final_message.split('/')[-1]

                self.textBrowser.append(name+":"+ chat)
                pass
            elif 'TN/' in self.final_message:
                try:
                    self.teacher = self.final_message.split('/')
                except:
                    pass
                print(self.teacher)
            elif 'success' in self.final_message:
                self.sock.send(f'{self.pw_change_new.text()}')

            elif 'mismatch' in self.final_message:
                QMessageBox.warning(self.pw_change_dialog,'비밀번호 오류','비밀번호를 다시 확인하세요.')
            elif 'checkback' in self.final_message:
                QMessageBox.warning(self.pw_change_dialog, '아이디 오류', '아이디를 다시 확인하세요')


    def quitmessage(self):
        self.sock.send('chat/그만하기'.encode())
        self.move_page('학생메인')

    def sendqna(self): # 질문 보내기
        sendData = f'Question/{self.send_line.text()}'
        self.sock.send(sendData.encode('utf-8'))
        self.send_line.clear()

    def consult(self): #상담요청 버튼
        self.TN = []
        self.sock.send('name_list/'.encode())
        time.sleep(0.3)
        try:
            for i in range(len(self.teacher)):

                self.TN.append(self.teacher[i + 1])
        except:
            pass

        item, ok = QInputDialog.getItem(self, "선생님 목록", "선생님을 선택하세요.", self.TN, 0, False)
        if ok and item:
            print('선생님이름:',item)
            self.sock.send(f'invite/{item}'.encode())

        if '수락' in self.final_message:
            self.move_page('상담방')
            self.TN.clear()


    def sendconsul(self): # 상담 메지시 보내기
        sendDataa = f'chat/{self.login_id}/{self.lineEdit.text()}'

        self.sock.send(sendDataa.encode('utf-8'))
        self.lineEdit.clear()

    def renew(self): # 질문 페이지 새로고침
        self.qnacount=0
        self.sock.send('QnA/'.encode())
        columnname = ['번호', '질문', '답변', '학생이름', '선생님이름']
        self.qna_table.setHorizontalHeaderLabels(columnname)
        self.qna_table.setRowCount((self.qnacount + 1))

        for i in range(self.i):

            self.qna_table.setItem(i, 0, QTableWidgetItem(globals()['lst{}'.format(i)][0]))
            self.qna_table.setItem(i, 1, QTableWidgetItem(globals()['lst{}'.format(i)][1]))
            self.qna_table.setItem(i, 2, QTableWidgetItem(globals()['lst{}'.format(i)][2]))
            self.qna_table.setItem(i, 3, QTableWidgetItem(globals()['lst{}'.format(i)][3]))
            self.qna_table.setItem(i, 4, QTableWidgetItem(globals()['lst{}'.format(i)][4]))
            print('i:', i)

        self.i=0
        self.qna_table.clear()


    def overlapCheck(self): #중복확인
        self.sign_id = self.join_id_edit.text()  # 회원가입 ID lineEdit 값 가져오기
          # 회원가입 PW lineEdit 값 가져오기
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
        self.login_id = self.login_id_edit.text()  # 로그인 ID lineEdit 값 가져오기
        self.login_pw = self.login_pw_edit.text()  # 로그인 PW lineEdit 값 가져오기
        self.sock.send(f"{'login/' +'student/'+ self.login_id + '/' + self.login_pw}".encode())  # 로그인/ID/PW
        print('아이디:',self.login_id)
        recv_message = self.sock.recv(4096).decode()
        print('로그인 메시지: ', recv_message)
        if '!OK' in recv_message:
            self.move_page('학생메인')
        else:
            pass

    def SignUp(self):# 회원가입 함수
        QMessageBox.information(self, '회원가입', '회원가입 성공!.')
        self.sign_pw = self.join_pw_edit.text()
        self.nickname = self.join_name_edit.text()
        self.move_page('로그인')
        self.sock.send(f'{self.sign_id}/{self.sign_pw}/{self.nickname}'.encode('utf-8'))
        print('')

    def move_page(self, page): # 페이지 이동 함수
        if page == '로그인':
            self.stackedWidget_2.setCurrentWidget(self.login_page_2)
        elif page == 'QnA/':
            self.sock.send('QnA/'.encode())
            # self.qna_table.setRowCount(0)
            self.qnacount=0
            self.qna_table.clear()

            self.stackedWidget_2.setCurrentWidget(self.qna_page_2)

        elif page == '학생메인':
            self.stackedWidget_2.setCurrentWidget(self.student_main_page)
            receiver = Thread(target=self.receive_messages, args=(self.sock,))  # 수신 스레드
            receiver.start()
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
        elif page=='상담방':

            self.stackedWidget_2.setCurrentWidget(self.consulting_page)

        elif page == '문제풀기':
            self.rowcounts=0
            try:
                self.insql(f'delete from 문제집')  # 쿼리문 작성
            except:
                pass
            self.stackedWidget_2.setCurrentWidget(self.student_quiz)
        elif page == '회원가입':
            self.stackedWidget_2.setCurrentWidget(self.register_page_2)


    def solv_page(self): # 문제 페이지
        self.sock.send("quiz/".encode())

        self.move_page('문제풀기')

    def uploadques(self): # 문제 업로드 하기
        self.rowcounts=0
        self.sock.send('quiz/'.encode())

        pass
    def check_answer(self): # 답 비교하기 함수
        self.score=0
        self.wrong_answer.clear() # 틀린답 리스트 지우기
        self.check_browser.clear() # 오답표시 브라우저
        print('self.answer_lst: ',self.answer_lst)
        answer_lst=[]
        for i in range(self.tableWidget_2.rowCount()):
            try:
                item = self.tableWidget_2.item(i,1)
                value = item.text()
            except:
                value=''
            answer_lst.append(value)
            print("답 쓴거:",answer_lst)

            if self.answer_lst[i]==answer_lst[i]: # 답이 정답이면 스코어 증가 answer/문제 로 정답 메시지 보내기
                self.score+=1
                self.sock.send(f'mark/{i + 1}/o'.encode())
            else:
                self.wrong_answer.append(i+1) # 답이 오답이면 스코어 증가 x wrong/문제로 오답 메시지 보내기
                self.check_browser.append(f'{i+1} 오답')
                self.sock.send(f'mark/{i + 1}/x'.encode())

        self.lcdNumber.display(self.score) # lcd 위젯 점수 표시용
        # self.sock.send(f'{self.log}')
        print('final answer_lst: ', answer_lst)
        print(self.wrong_answer)
        self.answer_lst.clear()

    def save(self): # 작성한 문제 저장하기
        prob=[]
        ans=[]
        print(self.login_id)
        try:
            self.insql(f'drop table {self.login_id}')
        except:
            pass
        with self.con:
            cur=self.con.cursor()
            cur.execute(f'create table {self.login_id} (문제 TEXT,답 TEXT)')

        for i in range(self.tableWidget_2.rowCount()):
            try:
                item1=self.tableWidget_2.item(i,0)
                value1=item1.text()
                item2= self.tableWidget_2.item(i,1)
                value2 = item2.text()
            except:
                value2='' # 아무것도 적지 않으면 오류가 뜨기에 예외처리를 통해서 ''로 변경해주기

            prob.append(value1)
            ans.append(value2)

        print(prob)
        print(ans)
        for j in range(len(ans)):

             self.insql(f'insert into {self.login_id} values ("{prob[j]}","{ans[j]}")')
        # with self.con:
        #
        #     cur=self.con.cursor()
        #     cur.execute('')

    def load(self): # 불러오기
        i=0
        rowcount=0
        with self.con:
            cur=self.con.cursor()
            rows=cur.execute(f'select * from {self.login_id}')
            for row in rows:
                rowcount += 1
                self.tableWidget_2.setRowCount((rowcount))

                print(row[0])

                for j in range(self.tableWidget_2.rowCount()):
                    self.tableWidget_2.setItem(i,0,QTableWidgetItem(row[0]))
                    self.tableWidget_2.setItem(i,1,QTableWidgetItem(row[1]))
                i += 1



    def pw_change(self):
        # super().__init__()
        self.pw_change_dialog.setWindowTitle('비밀번호 변경하기')
        self.pw_change_dialog.setWindowModality(Qt.ApplicationModal)
        self.pw_change_dialog.resize(400, 300)

        self.pw_change_line1=QLabel('ID: ',self.pw_change_dialog)
        self.pw_change_line2=QLabel('현재 PW: ',self.pw_change_dialog)
        self.pw_change_line3=QLabel('변경할 PW: ',self.pw_change_dialog)
        self.pw_change_line1.setGeometry(50, 50, 100, 30)
        self.pw_change_line2.setGeometry(50, 90, 100, 30)
        self.pw_change_line3.setGeometry(50, 130, 100, 30)

        self.pw_change_id=QLineEdit(self.pw_change_dialog)
        self.pw_change_pw=QLineEdit(self.pw_change_dialog)
        self.pw_change_new=QLineEdit(self.pw_change_dialog)

        self.pw_change_id.setGeometry(170, 50, 100, 30)
        self.pw_change_pw.setGeometry(170, 90, 100, 30)
        self.pw_change_new.setGeometry(170, 130, 100, 30)

        self.pw_change_check_btn=QPushButton('check',self.pw_change_dialog)
        self.pw_change_quit_btn=QPushButton('나가기',self.pw_change_dialog)

        self.pw_change_check_btn.setGeometry(290,50,80,30)
        self.pw_change_quit_btn.setGeometry(170,200,60,30)


        try:
            print('다이얼',self.final_message)
        except:
            pass

        self.pw_change_check_btn.clicked.connect(lambda :self.sock.send(f'pw_change/{self.pw_change_id.text()}/{self.pw_change_pw.text()}'.encode()))
        self.pw_change_quit_btn.clicked.connect(lambda :self.pw_change_dialog.close())

        self.pw_change_dialog.show()




if __name__ == '__main__':
    # Data()

    app = QApplication(sys.argv)
    ex = MainStudent()
    ex.show()
    app.exec()