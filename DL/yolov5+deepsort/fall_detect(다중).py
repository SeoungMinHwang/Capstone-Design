import torch
import cv2
import numpy as np
import time

from collections import deque, defaultdict

class YoloDetector():

    def __init__(self, model_name):
        self.model = self.load_model(model_name)
        self.classes = self.model.names
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("Using {} device".format(self.device))


    def load_model(self, model_name):
        if model_name:
            model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_name) # force_reload=True -> 기존 캐시를 삭제하여 PyTorch 허브에서 최신 Yolov5 버전을 새로 다운로드 해서 가져옴
        else:
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        return model    

    # 1FPS에 해당하는 평균신뢰도를 구하는 함수
    def calculate_average_confidence(self, id: dict) -> list:
        average_confidence = []
    
        for key, conf_list in id.items():
            if len(conf_list) > 0:
                average_confidence.append(sum(conf_list) / len(conf_list))
                
        print(average_confidence)
        
        return average_confidence 
        # ex) object가 3개 있는 경우 [0.65, 0.90, 0.56] 
            
    

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

detector = YoloDetector(model_name='best.pt')

# 이전 시간, 프레임 카운트 초기화
prev_time = time.time()

flag = False

count = 0

average_confidence_list = deque()

# 앞에 몇개씩 건너 뛸건지(밀건지) 설정
window_size = 1

# object id : conf_list
id_conf_list = defaultdict(list)

# object id : avg_conf_list
id_avg_list = defaultdict(deque)

while True:
    
    succes, frame = cap.read()
    start = time.perf_counter()
    
    
    if not succes:
        break
    
    results = detector.model(frame)
    detections = results.pandas().xyxy[0].values.tolist()
    # print(detections)
    
    # 각각의 detect된 id별로 신뢰도를 따로 저장함
    for i in range(len(detections)):
        id_conf_list[i+1].append(detections[i][4])
        # ex) id = {1:[0.54], 2:[0.66]}
    # print() 
        # conf_list.append(detections[i][4])
        
    # print(detections) # [[312.89031982421875, 226.67625427246094, 985.8556518554688, 718.7860107421875, 0.8764397501945496, 0, 'person']]

    
    # 결과 시각화
    for result in results.xyxy[0]:
        x1, y1, x2, y2, conf, cls = result
        
        if conf > 0.6:
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, f'{detector.classes[0]} {conf:.2f}', (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    
    # FPS 계산 및 신뢰도 평균 출력 (1초마다 평균신뢰도를 구함)
    current_time = time.time()
    if current_time - prev_time >= 1.0:
        average_confidence = detector.calculate_average_confidence(id_conf_list)

        if average_confidence: 
            
            # 개별 object에 대한 ex) [0.65, 0.90, 0.56] ---> 화면에서 detect 됬다가 사라지는 현상은 어떻게 처리할것인가???(문제) 0값으로 처리해야함
            for i in range(len(average_confidence)):
                print("1초마다 평균 신뢰도: {:.2f}".format(average_confidence[i]))
                id_avg_list[i+1].append(average_confidence[i])
            
                # 5회에 대한 평균 계산 (슬라이딩 윈도우 방식)
                if len(id_avg_list[i+1]) >= 5:
                    average_5fps_confidence = sum(id_avg_list[i+1]) / len(id_avg_list[i+1])
                    print("5회에 대한 평균 신뢰도: {:.2f}".format(average_5fps_confidence))
                    
                    # 탐지알림 기준 정하기 (한 화면에 여러개의 object가 쓰러질때 매번 알림주지 않고, 1회만 주기위해 flag설정)
                    if average_5fps_confidence > 0.7:
                        count += 1
                        flag = True
                    
                    # 얼마나 건너뛸지(밀지) 설정
                    for _ in range(window_size):
                        id_avg_list[i+1].popleft()    
                
                    
            print(id_avg_list[1], len(id_avg_list[1]))
        
        if flag:
            print(f'@@TEST. {count}명의 쓰러짐이 탐지되었습니다(알림보내기)@@')
            
        # 초기화
        prev_time = current_time
        id_conf_list = defaultdict(list)
        flag = False                        # 한 화면에서 여러개의 object가 쓰러져도 한번만 알림을 보내기 위함
        count = 0                           # 몇명이 쓰러졌는지 

     
    end = time.perf_counter()
    totalTime = end - start
    fps = 1 / totalTime
    
    cv2.putText(frame, "FPS: " + str(int(fps)), (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)
    cv2.imshow('img', frame)

    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    

    

cap.release()
cv2.destroyAllWindows()
