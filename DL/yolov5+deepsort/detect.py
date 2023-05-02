
import torch
import cv2
import numpy as np
import time


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
    
    
    def score_frame(self, frame):
        self.model.to(self.device)
        downscale_factor = 2
        width = int(frame.shape[1] / downscale_factor)
        height = int(frame.shape[0] / downscale_factor)
        frame = cv2.resize(frame, (width, height))
        
        results = self.model(frame)
        # crops = results.crop(save=True)
        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        
        return labels, cord
    
    
    def class_to_label(self, x):
        return self.classes[int(x)]
    

    def plot_boxes(self, results, frame, height, width, confidence=0.3):
        lables, cord = results
        detections = []
        
        n = len(lables)
        x_shape, y_shape = width, height
        
        for i in range(n):
            row = cord[i]
            
            if row[4] >= confidence:
                x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)

                if self.class_to_label(lables[i]) == 'person':
                    # x_center = x1 + (x2 - x1)
                    # y_center = y1 + ((y2 - y1) / 2)
                    # tlwh = np.asarray([x1, y1, int(x2 - x1), int(y2 - y1)], dtype=np.float32)
                    confidence = float(row[4].item())
                    # feature = 'person'
                    detections.append(([x1, y1, int(x2 - x1), int(y2 - y1)], row[4].item(), 'person'))
        return frame, detections


cap = cv2.VideoCapture(0)


cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


detector = YoloDetector(model_name='last.pt')

import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'


from deep_sort_realtime.deepsort_tracker import DeepSort

object_tracker = DeepSort(max_age=10,                    # 객체가 추적 리스트에서 유지되는 최대 시간. 기본값 70
                          n_init=5,                     # 새로운 객체를 추적하기 위해 필요한 최소 측정값. 기본값 3
                          nms_max_overlap=1.0,          # Non-maxima suppression(NMS)에서 중복 검출을 위한 최대 겹침 비율. 기본값 1.0
                          max_cosine_distance=0.3,      
                          nn_budget=None,               # Nearest Neighbor 버퍼의 크기, 기본값 None
                          override_track_class=None,    # 클래스 간 추적 정보를 전달하기 위한 클래스
                          embedder="mobilenet",         # 객체 임베딩을 생성하기 위해 사용할 임베더 모델
                          half=True,                    # 모델의 가중치를 half-precision(16-bit)로 사용할지 여부
                          bgr=True,                     # 입력 이미지를 BGR 형식으로 변환할지 여부, 기본값 False임
                          embedder_gpu=False,           # 임베더 모델을 GPU로 실행할지 여부. 기본값은 False임
                          embedder_model_name=None,     # 임베딩 모델의 이름. 기본값은 None임
                          embedder_wts=None,            # 임베딩 모델의 가중치. 기본값은 None임
                          polygon=False,                # 트랙을 표시할 때 다각형 형태로 표시할지 여부. 기본값은 False임
                          today=None)




while True:
    # 모델 추론 시간 간격을 조정하는 방법(최적화 방법?)
    start_time = time.time()

    # 프레임 읽기
    succes, img = cap.read()
    
    start = time.perf_counter()
    
    if not succes:
        break
    
    results = detector.score_frame(img)
    print(results) # (tensor([0.]), tensor([[0.21100, 0.34878, 0.73225, 1.00000, 0.89594]])) -> (labels, cord(좌표, 신뢰도))
    
    img, detections = detector.plot_boxes(results, img, height=img.shape[0], width=img.shape[1], confidence=0.4)
    # print(img, detections)

    
    tracks = object_tracker.update_tracks(detections, frame=img)
    # print(tracks)

    for track in tracks:
        if not track.is_confirmed():
            continue
        
        track_id = track.track_id
        print(track_id)
        ltrb = track.to_ltrb()
        
        bbox = ltrb
        
        cv2.rectangle(img, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 0, 255), 2)
        cv2.putText(img, "ID: " + str(track_id), (int(bbox[0]), int(bbox[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        

    end = time.perf_counter()
    totalTime = end - start
    fps = 1 / totalTime
    
    cv2.putText(img, "FPS: " + str(int(fps)), (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)
    cv2.imshow('img', img)
    
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    elapsed_time = time.time() - start_time
    
    if elapsed_time < 0.1:
        time.sleep(0.1 - elapsed_time)
    
    

cap.release()
cv2.destroyAllWindows()



