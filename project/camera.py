import cv2

def camera_start():
    camera1 = cv2.VideoCapture(0)
    camera2 = cv2.VideoCapture(2)
    # camera = cv2.VideoCapture('http://192.168.35.226:8000/stream.mjpg')
    camera3 = cv2.VideoCapture(1)

    return camera1,camera2,camera3
