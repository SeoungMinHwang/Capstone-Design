

# -------------------------------------------------
import serial
import RPi.GPIO as GPIO
import time
import spidev
from socket import *
import threading
from flask import Flask, render_template, Response, request



print("\n실행\n")
currentStep = 1
oldStep = 0
uartString = ""
uartLength = 0
    
startBit = 0xf0
commandBit = 0xa1
roll = 100
pitch = 100
yaw = 100
throttle = 0
operationBit = 0x05
checkSum = 0

firstRoll = 0
firstPitch = 0

        # 추가 변수
gogo = 0

drone_state = True  # 드론 이동 가능 상태

dmove_direction = ""  # 이동방향
fall_detect = False  # 감지했는지

drone_move = False  # 드론이 이동중인지

goDronego = False
switch_list = [22, 27, 17, 23, 24, 25]

# #드론 자동 이동
# #--------------------------------------------------------
def start_Drone():
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=0.001)
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = 1000000

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    global currentStep
    global oldStep
    global uartString
    global uartLength 
    
    global startBit 
    global commandBit 
    global roll 
    global pitch 
    global yaw
    global throttle
    global operationBit 
    global checkSum 

    global firstRoll 
    global firstPitch 

        # 추가 변수
    global gogo 

    global drone_state

    global dmove_direction
    global fall_detect

    global drone_move 

    global goDronego
    global switch_list

    
    def checkNextStep():
        global currentStep
        global oldStep
        global uartString

        time.sleep(0.3)
        uartString = ""
        oldStep = currentStep
        currentStep = 0

    def checkCrLfProcess():
        global currentStep
        global oldStep
        global uartString
        global uartLength

        while ser.inWaiting():
            uartString += ser.read().decode()
            uartLength = len(uartString)
            if uartLength > 4 and uartString.find("\r\n", 0, 2) == 0 \
                    and uartString.find("\r\n", uartLength-2) == uartLength - 2:
                currentStep = oldStep
                currentStep += 1
                break

    def analog_read(channel):
        data = spi.xfer2([1, (0x08 + channel) << 4, 0])
        adc_out = ((data[1] & 0x03) << 8) + data[2]
        time.sleep(0.04)

        return adc_out

    def checkThrottle():
        global drone_move
        drone_move = True
        global throttle
        global pitch

        if drone_move:
            if throttle < 20:
                throttle = 20
            elif throttle < 120:
                throttle += 20

        # 하강
        # if GPIO.input(switch_list[1]) == 0:
        #     if throttle > 59:
        #         throttle -= 20
        #     elif throttle > 3:
        #         throttle -= 4
        # #
        # #상승
        # if GPIO.input(switch_list[0]) == 0:
        #     if throttle < 20:
        #        throttle = 20
        #     elif throttle < 181:
        #         throttle += 20

    # 전진 후진

    def checkPitch():
        global pitch
        global throttle

        global firstPitch

        secondPitch = analog_read(3)

        if secondPitch < firstPitch - 450:
            pitch = 75
        elif secondPitch < firstPitch - 350:
            pitch = 80
        elif secondPitch < firstPitch - 250:
            pitch = 85
        elif secondPitch < firstPitch - 150:
            pitch = 90
        elif secondPitch < firstPitch - 50:
            pitch = 95
        elif secondPitch < firstPitch + 50:
            pitch = 100
        elif secondPitch < firstPitch + 150:
            pitch = 105
        elif secondPitch < firstPitch + 250:
            pitch = 110
        elif secondPitch < firstPitch + 350:
            pitch = 115
        elif secondPitch < firstPitch + 450:
            pitch = 120
        else:
            pitch = 125

    # 좌우 이동
    def checkRoll():
        global roll
        global firstRoll

        secondRoll = analog_read(2)

        if secondRoll < firstRoll - 450:
            roll = 75
        elif secondRoll < firstRoll - 350:
            roll = 80
        elif secondRoll < firstRoll - 250:
            roll = 85
        elif secondRoll < firstRoll - 150:
            roll = 90
        elif secondRoll < firstRoll - 50:
            roll = 95
        elif secondRoll < firstRoll + 50:
            roll = 100
        elif secondRoll < firstRoll + 150:
            roll = 105
        elif secondRoll < firstRoll + 250:
            roll = 110
        elif secondRoll < firstRoll + 350:
            roll = 115
        elif secondRoll < firstRoll + 450:
            roll = 120
        else:
            roll = 125

    def drone():
        global drone_move
        global gogo
        if drone_move == True:

            gogo += 1
            if gogo >= 15:

                drone_move = False

    # 좌우 회전

    def checkYaw():
        global yaw

        # if GPIO.input(switch_list[2]) == 0:
        #     yaw = 50
        # elif GPIO.input(switch_list[3]) == 0:
        #     yaw = 150
        # else:
        yaw = 100

    # 위급상황시(정지버튼)
    def checkEmergency():
        global roll
        global pitch
        global yaw
        global throttle
        # switch_list = [22, 27, 17, 23, 24, 25]
        # if GPIO.input(switch_list[4]) == 0:
            # throttle = 0
            # roll = 100
            # pitch = 100
            # yaw = 100

    def sendDroneCommand():
        ser.write("at+writeh000d".encode())

        ser.write((hex(startBit)[2:4]).encode())
        ser.write((hex(commandBit)[2:4]).encode())
        ser.write((hex(roll)[2:4]).encode())
        ser.write((hex(pitch)[2:4]).encode())
        ser.write((hex(yaw)[2:4]).encode())

        if throttle < 0x10:
            ser.write(('0'+hex(throttle)[2:4]).encode())
        else:
            ser.write((hex(throttle)[2:4]).encode())

        ser.write(('0'+hex(operationBit)[2:4]).encode())

        if checkSum < 0x10:
            ser.write(('0'+hex(checkSum)[2:4]).encode())
        else:
            ser.write((hex(checkSum)[2:4]).encode())

        ser.write("\r".encode())

    def checkCRC():
        global commandBit
        global roll
        global pitch
        global yaw
        global throttle
        global operationBit
        global checkSum

        checkSum = commandBit + roll + pitch + yaw + throttle + operationBit
        checkSum = checkSum & 0x00ff

    print("사상자 발생")
    
    while True:
        # 드론을 출발할것인지에 대한 입력 받아오기
        # if drone_state and fall_detect:
        #     print("드론 출발합니다")
        #     checkNextStep()

        if currentStep == 0:
            print("드론 세팅")
            checkCrLfProcess()

        elif currentStep == 1:
            print("드론상태확인")
            if drone_state:
                ser.flushOutput()
                ser.flushInput()
                uartString = ""
                firstRoll = analog_read(2)
                firstPitch = analog_read(3)
                ser.write("atd".encode())
                ser.write("083a5c1f15d5".encode())
                ser.write("\r".encode())
                checkNextStep()

        elif currentStep == 2:
            print("드론연결확인")
            if uartString.find("\r\nOK\r\n", 0, 6) == 0:
                print("Wait Connect")
                checkNextStep()

            else:
                print("Connect 1 ERROR")
                uartString = ""
                currentStep = 100

        elif currentStep == 3:
            if uartString.find("\r\nCONNECT ", 0, 10) == 0:
                print("Connect OK")
                time.sleep(0.3)
                uartString = ""
                currentStep += 1
    # 확인
            else:
                print("Connect 2 ERROR")
                uartString = ""
                currentStep = 100
        # 버튼이 눌렸거나 높이 위험 확인 및 이동
        elif currentStep == 4:
            print("드론 출발")
            checkThrottle()  # 일정 높이 올라간 뒤 앞으로 이동
            checkPitch()
            # checkRoll()
            # checkYaw()
            checkEmergency()
            checkCRC()
            sendDroneCommand()
            time.sleep(0.1)
            drone()

            # if GPIO.input(switch_list[5]) == 0:
            if drone_move == False:
                print("Request Disconnect")
                time.sleep(1)
                ser.flushInput()
                uartString = ""
                ser.write("ath".encode())
                ser.write("\r".encode())
                drone_state = True
                checkNextStep()

        elif currentStep == 5:
            if uartString.find("\r\nOK\r\n", 0, 6) == 0:
                print("Wait Disconnect")
                checkNextStep()
                

            else:
                print("Disconnect 1 ERROR")
                uartString = ""
                currentStep = 100

        elif currentStep == 6:
            if uartString.find("\r\nDISCONNECT", 0, 12) == 0:
                print("Disconnect 1 OK")
                checkNextStep()

            else:
                print("Disconnect 2 ERROR")
                uartString = ""
                currentStep = 100

        elif currentStep == 7:
            if uartString.find("\r\nREADY", 0, 7) == 0:
                print("Disconnect 2 OK")
                time.sleep(0.3)
                uartString = ""
                currentStep = 1

            else:
                print("Disconnect 3 ERROR")
                uartString = ""
                currentStep = 100

        else:
            if ser.inWaiting():
                uartString = ""
                time.sleep(0.5)
                while ser.inWaiting():
                    uartString += ser.read().decode()

                print(uartString)
                uartString = ""

            uartString = input("Enter AT Command: ")
            ser.write(uartString.encode())
            ser.write("\r".encode())
            print("Wait Response Command for 3s...")
            time.sleep(3)

def send(sock):
    # while True:
    sendData = input('>>>')
    sock.send(sendData.encode('utf-8'))


def receive(sock):
    # while True:
    recvData = sock.recv(1024)
    print('상대방 :', recvData.decode('utf-8'))
    if (recvData.decode('utf-8') == "드론"):
        start_Drone()
    
            
def start_app():
    app = Flask(__name__)


    @app.route('/')
    def drone_but():
        return render_template('drone_but.html')
    @app.route('/drone', methods=['GET'])
    def drone_go():
        return open("Drone/Start_Drone.py")

    if __name__ == "__main__":
        app.run(debug=True, host='0.0.0.0', port=3000, threaded=True)
        
port = 8081

serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.setsockopt(SOL_SOCKET, SO_REUSEADDR,1)
serverSock.bind(('', port))
serverSock.listen(1)

print('%d번 포트로 접속 대기중...' % port)

connectionSock, addr = serverSock.accept()

print(str(addr), '에서 접속되었습니다.')

sender = threading.Thread(target=send, args=(connectionSock,))
receiver = threading.Thread(target=receive, args=(connectionSock,))
starter = threading.Thread(target=start_app, args=(connectionSock,))

sender.start()
receiver.start()
starter.start()

while True:
    time.sleep(1)
    pass
