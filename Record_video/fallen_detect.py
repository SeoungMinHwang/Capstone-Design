import torch
import cv2
import numpy as np
import kakao
import base64
import functools
import pymysql
import datetime



#  ^m   ^t  ^h ^}  ^d    ^u ^}^x   ^`  ^d
def auto_conn_disconn(original_func):
    @functools.wraps(original_func)
    def wrapper(*args, **kwargs):

        # ^}      ^w^p         ^b         ^d     ^d  ^j
        conn = pymysql.connect(host='orion.mokpo.ac.kr',port = 8391, user='remo>
        cursor = conn.cursor()
                             
         # ^d  ^v  ^u^|  ^u  ^h^x  ^k  ^v^i   ^`  ^d
        query_result = original_func(cursor, *args, **kwargs)


        #         ^b     ^|  ^k^h      ^k  ^{^d  ^t^t ^j      ^d  ^j
        conn.commit()
        conn.close()

        #                 ^x ^y^x
        return query_result

    return wrapper
                               
@auto_conn_disconn
def event_occurs(cursor):
    event_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    query = f"INSERT INTO FALLEVENT (cctvid, eventtime, eventtype, videoid, res>

    cursor.execute(query, (encoded_image,))

class YoloDetector():

    def __init__(self, model_name):
        self.model = self.load_model(model_name)
        self.classes = self.model.names
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using {} device".format(self.device))


    def load_model(self, model_name):
        if model_name:
            model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_name)
        else:
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        return model


detector = YoloDetector(model_name='best.pt')

average_confidence_list = deque([0,0,0,0,0])
average_5fps_confidence = 0


#  ^u^l    ^}^d         ^a ^|   ^|  ^u^|   ^h ^t   ^l     ^b      ^|^d ^u
while True:

    cap = cv2.VideoCapture("http://192.168.0.7:8000/stream.mjpg")
    succes, frame = cap.read()


    results = detector.model(frame)
    detections = results.pandas().xyxy[0].values.tolist()
    print(detections)
    print(average_confidence_list)
    if (len(detections)) > 0:

        average_confidence_list.append(detections[0][4])
        average_5fps_confidence += detections[0][4]
        average_5fps_confidence -= average_confidence_list.popleft()
    else:
        average_confidence_list.append(0)
        average_5fps_confidence -= average_confidence_list.popleft()



    if average_5fps_confidence >= 3:
        print('DETECTED!!!')
        kakao.sendToMeMessage('       ^l^` ^u^y 3 ^x   ^`  ^s  ^=   ^p   ^| ^c^}  ^k  ^f^m ^u^|      ^x   ^t ^~^m ^k^h ^k !')
        average_confidence_list = deque([0,0,0,0,0])
        average_5fps_confidence = 0


        for result in results.xyxy[0]:
            x1, y1, x2, y2, conf, cls = result

            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            #   ^u ^j
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            #   ^t  ^| ^u^|  ^}      ^` ^w^p  ^l^` ^u^|   ^t  ^`   ^x     ^h^x ^v^i   ^` ^j

            #   ^t  ^| ^u^|  ^}      ^`     ^l^l ^}   ^|   ^` ^~
            cv2.imwrite("boxed_image.jpg", frame)


            #  ^}      ^`     ^}   ^t ^t  ^u^x ^w    ^t ^}  ^d^h     ^m  ^}  ^d   ^|   ^` ^y^x
            image_bytes = frame.tobytes()

            # Base64  ^|  ^}   ^t ^t
            encoded_image = base64.b64encode(image_bytes)


            # ^}         ^}   ^|  ^t^t  ^d ^w^p   ^` ^~
            encoded_image_str = encoded_image.decode('utf-8')
            event_occurs()
