

import torch
import cv2
import numpy as np
import time


model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt')  # custom model
cap = cv2.VideoCapture(0)


while True:
    # 모델 추론 시간 간격을 조정하는 방법(최적화 방법 2)
    start_time = time.time()
    
    # 프레임 읽기
    ret, frame = cap.read()
    
    if not ret:
        break
    # 프레임 크기 절반으로 줄이기 (최적화 방법 1)
    # frame = cv2.resize(frame, dsize=(0, 0), fx=0.5, fy=0.5)

    # 이미지 전처리
    img = frame[:, :, ::-1]
    results = model(img)
    print(results)
    
    # 결과 시각화
    for result in results.xyxy[0]:
        x1, y1, x2, y2, conf, cls = result
        
        if conf > 0.5:
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 1)
            cv2.putText(frame, f'{model.names[int(cls)]} {conf:.2f}', (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            
            
    # 결과 동영상 저장
    cv2.imshow('frame', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    elapsed_time = time.time() - start_time
    
    if elapsed_time < 0.1:
        time.sleep(0.1 - elapsed_time)

cap.release()
cv2.destroyAllWindows()



