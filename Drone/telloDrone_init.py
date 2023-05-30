# from djitellopy import Tello
# import cv2, math, time

# tello = Tello()
# tello.connect()

# print(tello.get_battery())

# tello.streamon()
# frame_read = tello.get_frame_read()

# tello.takeoff()

# while True:
#     img = frame_read.frame
#     cv2.imshow("drone", img)

#     key = cv2.waitKey(1) & 0xff
#     if key == 27: # ESC
#         break
#     elif key == ord('w'):
#         tello.move_forward(30)
#     elif key == ord('s'):
#         tello.move_back(30)
#     elif key == ord('a'):
#         tello.move_left(30)
#     elif key == ord('d'):
#         tello.move_right(30)
#     elif key == ord('e'):
#         tello.rotate_clockwise(30)
#     elif key == ord('q'):
#         tello.rotate_counter_clockwise(30)
#     elif key == ord('r'):
#         tello.move_up(30)
#     elif key == ord('f'):
#         tello.move_down(30)

# tello.land()



# from flask import Flask, Response, render_template
# import cv2
# from djitellopy import Tello

# app = Flask(__name__)

# tello = Tello()
# tello.connect()
# tello.streamon()

# @app.route('/')
# def index():
#     return render_template('index.html')

# def gen():
#     while True:
#         frame = tello.get_frame_read().frame
#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @app.route('/video_feed')
# def video_feed():
#     return Response(gen(),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0',port=3000)




# from djitellopy import Tello
# import cv2, time

# tello = Tello()
# tello.connect()
# print(tello.get_battery())
# tello.streamon()

# tello.takeoff()

# checkpoint = 0


# time.sleep(2)
    
# # # 거리 센서 값을 확인하여 50cm 이상이면 계속 진행, 그렇지 않으면 착지
# # distance = tello.get_distance_tof()
# # if distance < 50:
# #     tello.move_back(10)
# #     checkpoint = 0


# frame_read = tello.get_frame_read()

# # Tello 드론 이동
# tello.move_forward(100)  # cm 단위


# # 카메라 영상을 화면에 출력
# while True:
#     # 카메라 영상 프레임 받아오기
#     frame = frame_read.frame

#     # 프레임 출력
#     cv2.imshow('Tello Camera', frame)

#     # ESC 키를 누르면 종료
#     if cv2.waitKey(1) == 27:
#         break

# # 카메라 스트리밍 중지
# tello.streamoff()
# tello.land()

# # OpenCV 창 닫기
# cv2.destroyAllWindows()



from djitellopy import Tello
import cv2

# Tello 객체 생성
tello = Tello()

# Tello 드론 연결
tello.connect()
print(tello.get_battery())
tello.streamon()
# Tello 드론 이륙
# tello.takeoff()

# 카메라 영상을 보여주기 위한 OpenCV 윈도우 생성
# cv2.namedWindow("Tello Cam", cv2.WINDOW_NORMAL)

# Tello 드론이 이동할 거리 (단위: cm)
distance = 100

# 카메라 영상을 실시간으로 보여주면서, Tello 드론을 앞으로 이동하고 일정 거리 이동 후 착지
while True:
    # 카메라 영상 받아오기
    frame = tello.get_frame_read().frame
    
    # OpenCV 윈도우에 카메라 영상 출력
    cv2.imshow("Tello Cam", frame)
    key = cv2.waitKey(1) & 0xff
    if key == 27:  # ESC 키를 누르면 종료
        break
    
    
    # Tello 드론 앞으로 이동
    # tello.move_forward(50)
    print(tello.get_distance_tof())
    # Tello 드론이 이동한 거리 측정
    # current_distance = tello.
    
    # print(current_distance)
    # # Tello 드론이 일정 거리 이동하면 착지
    # if current_distance >= distance:
    #     break

# Tello 드론 착지
# tello.land()
tello.streamoff()
# Tello 드론 연결 해제
tello.end()

# OpenCV 윈도우 종료
cv2.destroyAllWindows()
