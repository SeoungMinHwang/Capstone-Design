import cv2, pafy

def camera_start():
    # video = pafy.new(url='https://youtu.be/N2NtCIVPo2M', gdata=False)
    # best = video.getbestvideo(preftype = 'webm')

    camera1 = cv2.VideoCapture(0)
    camera2 = cv2.VideoCapture(2)
    # camera2 = cv2.VideoCapture('http://192.168.141.226:8000/stream.mjpg')
    # camera = cv2.VideoCapture('http://192.168.35.226:8000/stream.mjpg')
    camera3 = cv2.VideoCapture(1)
    # camera3 = cv2.VideoCapture('http://192.168.141.226:8000/stream.mjpg')
    camera4 = cv2.VideoCapture(1)
    camera5 = cv2.VideoCapture(1)
    camera6 = cv2.VideoCapture(1)
    

    return camera1,camera2,camera3,camera4,camera5,camera6