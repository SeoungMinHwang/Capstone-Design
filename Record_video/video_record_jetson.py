import pymysql
import functools

# 데코레이터 정의 부분 
def auto_conn_disconn(original_func):
    @functools.wraps(original_func)
    def wrapper(*args, **kwargs):
        
        #이 곳에 쿼리 날리기전 커넥트 
        conn = pymysql.connect(host='127.0.0.1',port = 3306, user='remote', password='1234', db='capstone', charset='utf8')
        cursor = conn.cursor()
        
        
        #선언한 함수 실행 부분 
        query_result = original_func(cursor, *args, **kwargs)
        
        
        # 쿼리 날렸으니 커밋 후 디스 커넥트 
        conn.commit()
        conn.close()
        
        # 쿼리 결과 반환
        return query_result
        
    return wrapper  


@auto_conn_disconn
def save_video(cursor, cctv_id, video_start, video_end, camera_quality, video_path):
    
    sql = f'''INSERT INTO VIDEOLINK (cctvid, videostart, videoend, cameraquality, videopath) 
    VALUES ({cctv_id}, '{video_start}', '{video_end}', '{camera_quality}', '{video_path}');'''
    
    cursor.execute(sql)

@auto_conn_disconn
def del_video(cursor):
    sql = '''DELETE FROM VIDEOLINK
        WHERE videostart < CURDATE() - INTERVAL 2 DAY;'''

    cursor.execute(sql)

import cv2
import datetime
import os
import shutil
import time

CCTV_ID = 1

basic_path = '/root/Capstone-Design/Record_video/video_data_jetson'

os.makedirs(f'{basic_path}', exist_ok=True)

def writeVideo():
    '''웹캠에서 스트리밍되는 영상을 ./Video_data/년/월/일/00시.avi로 한시간 단위로 저장하고 
    이틀(현재 설정해둔 값 2)이상된 영상들은 자동적으로 삭제하는 함수입니다.'''
    
    #RTSP를 불러오는 곳
    video_capture = cv2.VideoCapture('http://orion.mokpo.ac.kr:7911')
    
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
        currentTime = datetime.datetime.now() + datetime.timedelta(hours=-3)

        #현재 시간을 '년도 달 일 시간 분 초'로 가져와서 문자열로 생성
        fileName = currentTime.strftime(f'%H시%M분')  

        #파일 저장하기 위한 변수 선언
        dir_path = f'{basic_path}/{currentTime.strftime("%Y년%m월%d일")}'
        
        #비디오 저장 위치 폴더 생성 
        os.makedirs(dir_path, exist_ok=True)
        
        # 비디오 저장
        out = cv2.VideoWriter(f'{dir_path}/{fileName}.avi', fourcc, fps, (streaming_window_width, streaming_window_height))
        

        while  int(datetime.datetime.now().strftime('%M') )% 5 != 0 or int(datetime.datetime.now().strftime('%S')) != 0:
            ret, frame = video_capture.read()

            # 영상을 저장한다.
            out.write(frame)
        out.release()  # out 객체 해제

        print('영상 저장')  
        save_video(CCTV_ID, currentTime.strftime('%Y-%m-%d %H:%M:%S'), (datetime.datetime.now() + datetime.timedelta(hours=-3)).strftime('%Y-%m-%d %H:%M:%S'), "퀄리티 좋음", f'{dir_path}/{fileName}.avi')
        time.sleep(1)    

        # 시간이 지난 폴더 삭제하는 기능 추가 해야함 
        arr = os.listdir(basic_path)
        for i in arr:
            try:
                if (datetime.date.today() - datetime.date(int(i[:4]), int(i[5:7]), int(i[8:10]))).days > 2:
                    shutil.rmtree(f"{basic_path}/{i}/")
            except:
                pass
            
        # 삭제 쿼리 파이와 젯슨 둘 중 하나에서만 작성하면 됨
        del_video()

if __name__ == "__main__":
    writeVideo()
