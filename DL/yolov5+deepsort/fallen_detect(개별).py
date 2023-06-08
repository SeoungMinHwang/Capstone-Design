import torch
import cv2
import numpy as np
import time

from collections import deque

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
    def calculate_average_confidence(self, conf_list):
        print(conf_list)
        
        if len(conf_list) > 0:
            average_confidence = sum(conf_list) / len(conf_list)
            return average_confidence
        else:
            return 0.0
    

cap = cv2.VideoCapture(0)

# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

detector = YoloDetector(model_name='best.pt')

# 이전 시간, 프레임 카운트 초기화
prev_time = time.time()
conf_list = []

average_confidence_list = deque()

# 앞에 몇개씩 건너 뛸건지 설정
window_size = 1

# 알림을 주기적으로 한 번씩만 보내기 위함
flag = 1

while True:
    
    succes, frame = cap.read()
    # start = time.perf_counter()
    
    
    if not succes:
        break
    
    results = detector.model(frame)
    detections = results.pandas().xyxy[0].values.tolist()
    
    # 전체 화면에 두명이 쓰러질때는 ? --> 일단 화면에서 detect한 모든 쓰러짐에 대한 신뢰도를 전부 append 
    for i in range(len(detections)):
        conf_list.append(detections[i][4])
    # print(detections) # [[312.89031982421875, 226.67625427246094, 985.8556518554688, 718.7860107421875, 0.8764397501945496, 0, 'person']]

    
    # 결과 시각화
    # for result in results.xyxy[0]:
    #     x1, y1, x2, y2, conf, cls = result
        
    #     if conf > 0.5:
    #         cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
    #         cv2.putText(frame, f'{detector.classes[0]} {conf:.2f}', (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    
    # FPS 계산 및 신뢰도 평균 출력 (2초동안 측정된(2FPS에 해당하는) 신뢰도의 평균신뢰도를 구함)
    current_time = time.time()
    if current_time - prev_time >= 1.0:
        average_confidence = detector.calculate_average_confidence(conf_list)
        print("1초마다 평균 신뢰도: {:.2f}".format(average_confidence))
        
        # 5회에 대한 평균 계산 (슬라이딩 윈도우 방식)
        average_confidence_list.append(average_confidence)
        if len(average_confidence_list) >= 5:
            average_5fps_confidence = sum(average_confidence_list) / len(average_confidence_list)
            print("5회에 대한 평균 신뢰도: {:.2f}".format(average_5fps_confidence))
            
            
            if average_5fps_confidence >= 0.6:
                if flag == 1:
                    print('@@TEST.쓰러짐이 탐지되었습니다(알림보내기)@@')
                flag *= -1

            # 얼마나 건너뛸지 설정 (기본값 : window_size=2)
            for _ in range(window_size):
                average_confidence_list.popleft()       
                
        # 초기화
        prev_time = current_time
        conf_list = []

     
    # end = time.perf_counter()
    # totalTime = end - start
    # fps = 1 / totalTime
    
    # cv2.putText(frame, "FPS: " + str(int(fps)), (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)
    # cv2.imshow('img', frame)

    
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break
    

    

# cap.release()
# cv2.destroyAllWindows()
