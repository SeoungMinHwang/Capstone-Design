### 파일 설명

> 시범 파일
- **best.pt** : 이미지 사이즈 640 배치 32 에폭 20 1클래스 person detect
- **last.pt** : 이미지 사이즈 640 배치 64 에폭 100 1클래스 person detect
    - train 이미지 3721장, test 이미지 1002장

<br/>

- export.pkl : fastapi 쓰러진사람, 안쓰러진사람 이미지 분류 모델
- test_detect.py : yolov5 활용 단순히 detect만
- detect.py : yolov5 + deepsort -> yolov5에 트래킹 추가

