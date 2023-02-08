from indy_utils import indydcp_client as client
from indy_utils.indy_program_maker import JsonProgramComponent
import numpy as np
import time

from socket import *

serverSock = socket(AF_INET, SOCK_STREAM)  # 소켓 객체 생성 (어드레스 패밀리, 소켓 타입)
serverSock.bind(('192.168.0.8', 9012))
serverSock.listen(1)

robot_ip = "192.168.0.2"    # 예시 STEP IP 주소
robot_name = "NRMK-Indy7"   # IndyRP2의 경우 "NRMK-IndyRP2"
indy = client.IndyDCPClient(robot_ip, robot_name) # indy 객체 생성

####################################
# 함수 정의 npy
#################################### 

def joint_move_to_with_autoWait(a):
    indy.joint_move_to(a)
    while indy.get_robot_status()['movedone'] == 0:
        time.sleep(0.5)
    return 1

def task_move_by_with_autoWait(a):
    indy.task_move_by(a)
    while indy.get_robot_status()['movedone'] == 0:
        time.sleep(0.5)
    return 1

def endtool_do_with_wait(a='c', b=1):  # a는 'o'(open), 'c'(close): default는 'c'  , b는 기다리는 시간(default = 1초)
    if a=='o':
        indy.set_endtool_do(0,0)
    elif a=='c':
        indy.set_endtool_do(0,1)
    else:
        indy.set_endtool_do(0,1)
    time.sleep(1)
    return 1

connectionSock, addr = serverSock.accept()
print(str(addr)+'에서 접속이 확인되었습니다.')

indy.connect()

thing_label=1  # 나중에 물체 인식 프로그램에서 레이블을 받아와야 함.
               # 예: thing_label = object_detect_label_program()


# joint move 좌표
point01=[70.95, -46.98, -83.96, 0, -49.10, -19.05]  # 물건 집는 위치
point02=[-13.16, -24.6, -136.55, 0, -18.86, -103.16]  # 첫번째 바구니 놓는 위치
point03=[-9.84, -30.26, -122.38, 0, -27.39, -99.84]  # 두번째 바구니 놓는 위치
point04=[-7.81, -37.08, -106.36, 0, -36.58, -97.81]  # 세번째 바구니 놓는 위치


while True :
    di_val=indy.get_di()
    indy.set_do(8,1)

    data=connectionSock.recv(1024)
    print('받은 데이터 : ', data.decode('utf-8'))

    if di_val[0] == 1 :
        # [1] 물건 집기(3가지 품목, 총 6개 물품)
        # - 일단 한 가지 고정된 위치에서 집는 것으로 한다.
        # - 물품별로 레이블이 분류되면 집는 위치가 달라지게 추후 수정해야 함
        joint_move_to_with_autoWait(point01)
        endtool_do_with_wait('o')
        task_move_by_with_autoWait([ 0, 0, -0.05, 0, 0, 0])
        endtool_do_with_wait('c')
    elif di_val[1] == 1 :
        # [2] 물건 이동
        # - 물건마다 내려 놓는 위치가 다르다.
        if data.decode('utf-8')[0]=='0':
            joint_move_to_with_autoWait(point02)
        elif data.decode('utf-8')[0]=='1':
            joint_move_to_with_autoWait(point03)
        elif data.decode('utf-8')[0]=='2':
            joint_move_to_with_autoWait(point04)
        # [3] 물건 놓기(2단계로 고려)
        print(data.decode('utf-8'))
        endtool_do_with_wait('o')
    elif di_val[2] == 1 :
        indy.set_do(8,0)
        indy.disconnect()

indy.disconnect()