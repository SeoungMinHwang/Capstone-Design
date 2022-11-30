import cv2
import datetime
import os


os.makedirs(f'./Video_data', exist_ok=True)

def writeVideo():
    '''웹캠에서 스트리밍되는 영상을 ./Video_data/년/월/일/00시.avi로 한시간 단위로 저장하고 
    이틀(현재 설정해둔 값 2)이상된 영상들은 자동적으로 삭제하는 함수입니다.'''
    
    
    
    #RTSP를 불러오는 곳
    video_capture = cv2.VideoCapture('http://192.168.141.226:8000/stream.mjpg')
    
    # 웹캠 설정
    video_capture.set(3, 800)  # 영상 가로길이 설정
    video_capture.set(4, 600)  # 영상 세로길이 설정
    
    fps = 24
    # 가로 길이 가져오기
    streaming_window_width = int(video_capture.get(3))
    # 세로 길이 가져오기
    streaming_window_height = int(video_capture.get(4))  
    
    # DIVX 코덱 적용
    fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
    
    
    while 1:
        #현재시간 가져오기
        currentTime = datetime.datetime.now()

        #현재 시간을 '년도 달 일 시간 분 초'로 가져와서 문자열로 생성
        fileName = currentTime.strftime(f'%H시%M분')  

        #파일 저장하기 위한 변수 선언
        dir_path = f'./Video_data/{currentTime.strftime("%Y년%m월%d일")}'
        
        #비디오 저장 위치 폴더 생성 
        os.makedirs(dir_path, exist_ok=True)
        
        # 비디오 저장
        out = cv2.VideoWriter(f'{dir_path}/{fileName}.avi', fourcc, fps, (streaming_window_width, streaming_window_height))
        

        while  (datetime.datetime.now() - currentTime).microseconds < int(3e+8) and int(datetime.datetime.now().strftime('%M') )% 5 != 0:
            ret, frame = video_capture.read()

            # 영상을 저장한다.
            out.write(frame)
        out.release()  # out 객체 해제
        
        
        # 시간이 지난 폴더 삭제하는 기능 추가 해야함 
        arr = os.listdir('./Video_data/')
        for i in arr:
            try:
                if (datetime.date.today() - datetime.date(int(i[:4]), int(i[5:7]), int(i[8:10]))).days > 2:
                    shutil.rmtree(f"./Video_data/{i}/")
            except:
                pass


if __name__ == "__main__":
    writeVideo()