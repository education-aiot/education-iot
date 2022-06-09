##서버
from socket import *
from threading import *


class MultiChatServer:

    # 소켓을 생성하고 연결되면 accept_client() 호출
    def __init__(self):
        self.clients = []  # 접속된 클라이언트 소켓 목록
        self.in_out_check=[]  # 사람 접속확인
        self.final_received_message = ""  # 최종 수신 메시지
        self.s_sock = socket(AF_INET, SOCK_STREAM) #소켓
        self.ip = '' # ip
        self.port = int(input("포트를 입력하세요 : "))
        self.s_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) #포트를 사용 중 일때 에러를 해결하기 위한 구문

        self.s_sock.bind((self.ip, self.port))
        print("클라이언트 대기 중 ...")
        self.s_sock.listen(100)
        self.accept_client()


        # 연결 클라이언트 소켓을 목록에 추가하고 스레드를 생성하여 데이터를 수신한다

    def accept_client(self):
        while True:
            client = c_socket, (ip, port) = self.s_sock.accept()
            if client not in self.clients:
                self.clients.append(client)  # 접속된 소켓을 목록에 추가
            print(ip, ':', str(port), '가 연결되었습니다')
            cth = Thread(target=self.receive_messages,
                         args=(c_socket,))  # 수신 스레드
            cth.start()

    # 데이터를 수신하여 모든 클라이언트에게 전송한다
    def receive_messages(self, c_socket):
        while True:
            try:
                self.incoming_message = c_socket.recv(4096)

                if not self.incoming_message:  # 연결이 종료됨
                    break
            except:
                continue
            else:
                self.final_received_message = self.incoming_message.decode('utf-8')
                self.send_all_clients(c_socket)
                print(self.final_received_message)


        c_socket.close()

    #  모든 클라리언트에게 메시지 전송
    def send_all_clients(self, senders_socket):
        if 'student' in self.final_received_message or 'login' in self.final_received_message :
            self.final_received_message = '!OK'+self.final_received_message
        elif 'QnA' in self.final_received_message:
            a=self.final_received_message.split('QnA/')
            self.final_received_message=a[1]
        else:
            self.final_received_message = 'XXX'


        for client in self.clients:  # 목록에 있는 모든 소켓에 대해
            socket, (ip, port) = client


            try:
                socket.sendall(self.final_received_message.encode())
            except:  # 연결 종료
                pass




if __name__ == "__main__":
    MultiChatServer()