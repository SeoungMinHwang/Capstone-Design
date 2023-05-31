import cv2


# 카메라 주소 설정
def camera_start():
    # video = pafy.new(url='https://youtu.be/N2NtCIVPo2M', gdata=False)
    # best = video.getbestvideo(preftype = 'webm')

    # camera1 = cv2.VideoCapture(0)
    # camera1 = 'http://172.23.21.249:8888/stream.mjpg'
    # camera1 = cv2.VideoCapture('http://192.168.46.226:8000/stream.mjpg')
    # camera2 = 'http://172.23.21.249:8888/stream.mjpg'
    # camera2 = cv2.VideoCapture('http://192.168.46.226:8000/stream.mjpg')
    # camera2 = cv2.VideoCapture('http://192.168.55.226:8000/stream.mjpg')
    # camera3 = 'http://172.23.21.249:8888/stream.mjpg'
    # camera3 = cv2.VideoCapture('http://192.168.46.226:8000/stream.mjpg')
    # camera3 = cv2.VideoCapture('http://192.168.141.226:8000/stream.mjpg')
    camera1 = cv2.VideoCapture(0)
    camera2 = cv2.VideoCapture('http://orion.mokpo.ac.kr:7910/stream.mjpg')
    camera3 = cv2.VideoCapture('http://orion.mokpo.ac.kr:7911')
    camera4 = cv2.VideoCapture(1)
    camera5 = cv2.VideoCapture(1)
    camera6 = cv2.VideoCapture(1)
    # # camera4 = cv2.VideoCapture('http://192.168.46.226:8000/stream.mjpg')
    # camera5 = cv2.VideoCapture('http://192.168.46.226:8000/stream.mjpg')
    # camera6 = cv2.VideoCapture('http://192.168.46.226:8000/stream.mjpg')

    return camera1,camera2,camera3,camera4,camera5,camera6
