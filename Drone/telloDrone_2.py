import cv2
import numpy as np
import tensorflow as tf
from djitellopy import Tello
from tf_bodypix.api import download_model, load_model, BodyPixModelPaths

# BodyPix 모델 다운로드
bodypix_model = load_model(download_model(
    BodyPixModelPaths.MOBILENET_FLOAT_50_STRIDE_16))

# Tello 드론 객체 생성
drone = Tello()

# 카메라 스트리밍 시작
drone.streamon()

# OpenCV VideoWriter 객체 생성
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter('output.avi', fourcc, 30.0, (960, 720))

# 객체 탐지를 위한 TensorFlow 모델 로드
detection_model = tf.saved_model.load('ssd_mobilenet_v2_320x320_coco17_tpu-8/saved_model')

# 객체 탐지 결과에서 사람만 추출하기 위한 클래스 ID
person_class_id = 1

# 객체 탐지 함수
def detect_objects(image_np):
    # 입력 이미지를 numpy 배열에서 Tensor로 변환
    input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)

    # Tensorflow 모델의 예측 수행
    detections = detection_model(input_tensor)

    # 예측 결과에서 필요한 정보 추출
    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy()
                  for key, value in detections.items()}
    detections['num_detections'] = num_detections

    # 사람 클래스에 대한 정보 추출
    class_id = detections['detection_classes'].astype(np.uint8)
    scores = detections['detection_scores']

    # 사람 클래스에 해당하는 bounding box 추출
    person_boxes = detections['detection_boxes'][class_id == person_class_id]

    return person_boxes

# 영상 처리 루프
while True:
    # 드론으로부터 영상 프레임 받아오기
    frame = drone.get_frame_read().frame

    # 객체 탐지 수행
    boxes = detect_objects(frame)

    # 탐지된 사람들의 bounding box에 대해 세그먼트 수행
    for box in boxes:
        # bounding box 좌표 추출
        y_min, x_min, y_max, x_max = box
        x_min = int(x_min * frame.shape[1])
        x_max = int(x_max * frame.shape[1])
    y_min = int(y_min * frame.shape[0])
    y_max = int(y_max * frame.shape[0])

    # 사람 세그먼트 수행
    segmentation_mask, _ = bodypix_model.predict_single(frame[y_min:y_max, x_min:x_max])

    # 세그먼트된 결과를 원래 이미지 크기로 복원
    segmentation_mask = cv2.resize(segmentation_mask, (x_max - x_min, y_max - y_min))
    segmentation_mask = np.array(segmentation_mask * 255, dtype=np.uint8)

    # 원본 이미지에 세그먼트 결과 합성
    alpha = 0.5
    mask = cv2.cvtColor(segmentation_mask, cv2.COLOR_GRAY2BGR)
    result = cv2.addWeighted(frame[y_min:y_max, x_min:x_max], alpha, mask, 1 - alpha, 0)
    frame[y_min:y_max, x_min:x_max] = result

# 처리된 프레임을 파일에 저장하고, 화면에 보여줌
out.write(frame)
cv2.imshow('frame', frame)
if cv2.waitKey(1) & 0xFF == ord('q'):
    break
