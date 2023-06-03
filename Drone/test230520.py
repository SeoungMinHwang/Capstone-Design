import threading
import robomaster
from robomaster import robot
from robomaster import flight
import cv2
import numpy as np
import time
import datetime
import argparse
import math
import os
from flask import Flask, render_template, Response, request, redirect, url_for,session

robomaster.config.LOCAL_IP_STR = "192.168.10.2"

face_cascade = cv2.CascadeClassifier('C:\A_capston\Capstone-Design\Capstone-Design\Drone\cascades\data\haarcascade_frontalface_alt2.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()

dimensions = (960, 720)

UDOffset = 150



faceSizes = [1026, 684, 456, 304, 202, 136, 90]
acc = [500,250,250,150,110,70,50]

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=False)
parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                    help='** = required')
parser.add_argument('-d', '--distance', type=int, default=3,
    help='use -d to change the distance of the drone. Range 0-6')
parser.add_argument('-sx', '--saftey_x', type=int, default=100,
    help='use -sx to change the saftey bound on the x axis . Range 0-480')
parser.add_argument('-sy', '--saftey_y', type=int, default=55,
    help='use -sy to change the saftey bound on the y axis . Range 0-360')
parser.add_argument('-os', '--override_speed', type=int, default=1,
    help='use -os to change override speed. Range 0-3')
parser.add_argument('-ss', "--save_session", action='store_true',
    help='add the -ss flag to save your session as an image sequence in the Sessions folder')
parser.add_argument('-D', "--debug", action='store_true',
    help='add the -D flag to enable debug mode. Everything works the same, but no commands will be sent to the drone')

args = parser.parse_args()

if args.save_session:
    ddir = "Sessions"

    if not os.path.isdir(ddir):
        os.mkdir(ddir)

    ddir = "Sessions/Session {}".format(str(datetime.datetime.now()).replace(':','-').replace('.','_'))
    os.mkdir(ddir)

class FrontEnd(object):
    #초기
    def __init__(self):
        print("Starting")
        self.tl_drone = robot.Drone()
        
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 10
        self.face_detected = False
        self.moving_distance = 0

        self.send_rc_control = False
        
        self.drone_fin=False
        
    def run(self):
        print("Running")
        self.tl_drone.initialize()
        #버전확인
        version = self.tl_drone.get_sdk_version()
        print("Drone SDK Version: {0}".format(version))
        
        #배터리 확인
        tl_battery = self.tl_drone.battery
        battery_info = tl_battery.get_battery()
        print("Drone battery soc: {0}".format(battery_info))
        
        #LED
        self.tl_led = self.tl_drone.led
        self.tl_led.set_led(r=255, g=0, b=0)
        
        #거리 센서
        # t1_sensor = self.t1_drone.sensor
        
        
        #카메라
        tl_camera = self.tl_drone.camera
        tl_camera.start_video_stream(display=False)
        tl_camera.set_fps("high")
        tl_camera.set_resolution("high")
        tl_camera.set_bitrate(6)
        
        # frame_read = tl_camera.read_video_frame()
        
        
        #필요 변수
        OVERRIDE = False
        should_stop = False
        tDistance = args.distance
        oSpeed = args.override_speed
        
        # Safety Zone X
        szX = args.saftey_x

        # Safety Zone Y
        szY = args.saftey_y
        
        def lerp(a,b,c):
            return a + c*(b-a)
        
        # drone_con = self.tl_drone.is_connected()
        #키입력
        
        while not should_stop:
            frame_read = tl_camera.read_cv2_image(strategy="newest")
            if frame_read is None:
                frame_read.stop()
                break
            
                
                
            # print(t1_sensor.sub_distance())
            theTime = str(datetime.datetime.now()).replace(':','-').replace('.','_')

            frame = cv2.cvtColor(frame_read, cv2.COLOR_BGR2RGB)
            frameRet = frame_read
            
            frame = np.rot90(frame)
            # Listen for key presses
            k = cv2.waitKey(20)
            if k == 8:
                if not OVERRIDE:
                    OVERRIDE = True
                    print("OVERRIDE ENABLED")
                else:
                    OVERRIDE = False
                    print("OVERRIDE DISABLED")
                    
            gray  = cv2.cvtColor(frameRet, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=2)

            # Target size
            tSize = faceSizes[tDistance]

            # These are our center dimensions
            cWidth = int(dimensions[0]/2)
            cHeight = int(dimensions[1]/2)

            noFaces = len(faces) == 0            
           
            # print(drone_con)
            if k == 27:
                should_stop = True
                break
            
            #얼굴 탐지
            if OVERRIDE: 
                for (x, y, w, h) in faces:
                    # 
                    roi_gray = gray[y:y+h, x:x+w] #(ycord_start, ycord_end)
                    roi_color = frameRet[y:y+h, x:x+w]

                    # setting Face Box properties
                    fbCol = (255, 0, 0) #BGR 0-255 
                    fbStroke = 2
                    
                    # end coords are the end of the bounding box x & y
                    end_cord_x = x + w
                    end_cord_y = y + h
                    end_size = w*2

                    # these are our target coordinates
                    targ_cord_x = int((end_cord_x + x)/2)
                    targ_cord_y = int((end_cord_y + y)/2) + UDOffset

                    # This calculates the vector from your face to the center of the screen
                    vTrue = np.array((cWidth,cHeight,tSize))
                    vTarget = np.array((targ_cord_x,targ_cord_y,end_size))
                    vDistance = vTrue-vTarget
                    
                    cv2.rectangle(frameRet, (x, y), (end_cord_x, end_cord_y), fbCol, fbStroke)

                    # Draw the target as a circle
                    cv2.circle(frameRet, (targ_cord_x, targ_cord_y), 10, (0,255,0), 2)

                    # Draw the safety zone
                    cv2.rectangle(frameRet, (targ_cord_x - szX, targ_cord_y - szY), (targ_cord_x + szX, targ_cord_y + szY), (0,255,0), fbStroke)

                    # Draw the estimated drone vector position in relation to face bounding box
                    cv2.putText(frameRet,str(vDistance),(0,64),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)
                    
                if noFaces:
                    self.yaw_velocity = 0
                    self.up_down_velocity = 0
                    self.for_back_velocity = 0
                    print("NO Head")
                            
            cv2.circle(frameRet, (cWidth, cHeight), 10, (0,0,255), 2)

            dCol = lerp(np.array((0,0,255)),np.array((255,255,255)),tDistance+1/7)
            
            if OVERRIDE:
                show = "OVERRIDE: {}".format(oSpeed)
                dCol = (255,255,255)
            else:
                show = "AI: {}".format(str(tDistance))

            # Draw the distance choosen
            cv2.putText(frameRet,show,(32,664),cv2.FONT_HERSHEY_SIMPLEX,1,dCol,2)

            # Display the resulting frame
            cv2.imshow(f'Tello Tracking...',frameRet)
            
            ret, buffer = cv2.imencode('.jpg', frameRet)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                
        cv2.destroyAllWindows()
        tl_camera.stop_video_stream()

        self.tl_drone.close()
        
    def droneMove(self):
        #이동
        if self.drone_fin == False :
            self.drone_fin=True
            tl_flight = self.tl_drone.flight
            tl_flight.takeoff().wait_for_completed() #이륙
            # tl_flight.forward(distance=100).wait_for_completed() #앞뒤 좌우 50이동
            tl_flight.land().wait_for_completed() #착륙
            
            
        # tl_flight.rotate(angle=180).wait_for_completed() #+-180도회전
        # tl_flight.rotate(angle=-180).wait_for_completed()
        
        # tl_flight.forward(distance=50).wait_for_completed() #앞뒤 좌우 50이동
        # tl_flight.backward(distance=50).wait_for_completed()
        # tl_flight.left(distance=50).wait_for_completed()
        # tl_flight.right(distance=50).wait_for_completed()
        
        # tl_flight.up(distance=20).wait_for_completed() #20cm 상승 하강
        # tl_flight.down(distance=20).wait_for_completed()
        
        # tl_flight.go(x=100, y=100, z=30, speed=30).wait_for_completed() #지정장소 이동
        # tl_flight.go(x=-100, y=-100, z=-30, speed=30).wait_for_completed()
        
        # tl_flight.curve(x1=60, y1=60, z1=0, x2=120, y2=0, z2=30, speed=30).wait_for_completed() #곡선비행
        # tl_flight.curve(x1=-60, y1=60, z1=0, x2=-120, y2=0, z2=-30, speed=30).wait_for_completed()
        
        # tl_flight.rc(a=20, b=0, c=0, d=0)@좌이 우이가 뭔데
        # time.sleep(4)
        # tl_flight.rc(a=-20, b=0, c=0, d=0)
        # time.sleep(3)
        # tl_flight.rc(a=0, b=0, c=0, d=0)
        
        #미션패드
        # tl_flight.mission_pad_on()
        # tl_flight.mission_pad_off()
        
       
        
    #드론 정보 및 높이
    def sub_tof_info_handler(tof_info):
        tof = tof_info
        print("drone tof: {0}".format(tof))
        
    def sub_drone_info_handler(drone_info):
        high, baro, motor_time = drone_info
        print("drone info: high:{0}, baro:{1}, motor_time:{2}".format(high, baro, motor_time))
        
    def sub_battery_info_handler(battery_info):
        battery_soc = battery_info
        print("Drone battery: soc {0}".format(battery_soc))


frontend = FrontEnd()        
def main():
    # 스레드 객체 생성
    run_thread = threading.Thread(target=frontend.run)
    drone_move_thread = threading.Thread(target=frontend.droneMove)

    # 스레드 실행
    run_thread.start()
    drone_move_thread.start()

    # 스레드가 종료될 때까지 대기
    run_thread.join()
    drone_move_thread.join()

    # run frontend
    # frontend.run()

app = Flask(__name__)

@app.route("/takeoff")
def takeoff():
  # 드론을 이륙시킵니다.
#   drone.takeoff()

    main()
#   return "드론 이륙"

@app.route("/land")
def land():
  # 드론을 착륙시킵니다.
#   drone.land()
    print("Land")
#   return "드론 착륙"

@app.route("/take_video")
def take_video():
    thread = threading.Thread(target=frontend.run)
    thread.start()
    return Response(frontend.run(), mimetype='multipart/x-mixed-replace; boundary=frame', headers={'Cache-Control': 'no-cache'})
    
    
if __name__ == "__main__":
    main()
    # app.run(debug=True, host='0.0.0.0', port=3000, threaded=True)
