from flask import Flask, render_template, Response, request, redirect, url_for,session
import requests
import cv2, camera, kakao, pymysql
from weather_search import get_weather_daum, job
import requests
from bs4 import BeautifulSoup
import jsonify
import json

conn = pymysql.connect(host='127.0.0.1', user='root', password='1234', db='capstone', charset='utf8')
cur = conn.cursor()
cur.execute('SELECT * FROM eventt')
eventlist = cur.fetchall()
cur.execute('SELECT * FROM Response')
responselist = cur.fetchall()
cur.execute('select * from drone')
dronelist = cur.fetchall()

app = Flask(__name__)
app.secret_key='daemeolikkakkala'
camera1,camera2,camera3,camera4,camera5,camera6 = camera.camera_start()

# camera = cv2.VideoCapture('http://192.168.35.226:8000/stream.mjpg')
# camera1 = cv2.VideoCapture(0)
# camera2 = cv2.VideoCapture('http://192.168.35.226:8000/stream.mjpg')
# camera3 = cv2.VideoCapture(1)

# 영상 긁어오기
def gen_frames(camera):
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# 지역에 따른 response연결
@app.route('/video_feed/<string:cctv_section>')
def video_feed(cctv_section):
    if cctv_section=='남악1':
        return Response(gen_frames(cv2.VideoCapture(camera1)), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif cctv_section=='남악2':
        return Response(gen_frames(cv2.VideoCapture(camera2)), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif cctv_section=='목포대1':
        return Response(gen_frames(cv2.VideoCapture(camera3)), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif cctv_section=='목포대2':
        return Response(gen_frames(camera4), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif cctv_section=='하당1':
        return Response(gen_frames(camera5), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif cctv_section=='하당2':
        return Response(gen_frames(camera6), mimetype='multipart/x-mixed-replace; boundary=frame')

# CCTV상세정보
@app.route('/detail')
def detail():
    if 'username' in session:
        sec = request.args.get('section')
        weather_list = get_weather_daum('전라남도 무안군 청계면')
        return render_template('detail.html', eventlist = eventlist, responselist = responselist, dronelist = dronelist, sec=sec, weather_list=weather_list )
    else:
        return redirect(url_for('login'))

# 로그인페이지
@app.route('/login')
@app.route('/')
def login():
    return render_template('login.html')

# 전체CCTV
@app.route('/all_cctv')
def all_cctv():
    if 'username' in session:
    # CCTV 지역 리스트
        cctv_list = ['공대1,2호관','공대3호관','공대4호관','공대5호관']
        return render_template('all_cctv.html',cctv_list=cctv_list)
    else:
        return redirect(url_for('login'))
    
# CCTV큰 화면
@app.route('/big_screen')
def big_screen():
    if 'username' in session:
        sec = request.args.get('section')
        return render_template('big_screen.html', sec=sec)
    else:
        return redirect(url_for('login'))

#카카오톡 보내기페이지
@app.route('/kakaosend')
def kakaosend():
    return render_template('kakao.html')


@app.route('/drone_but')
def drone_but():
    return render_template('drone_but.html')

# 사용자 확인
@app.route("/login_confirm",methods=['POST'])
def login_confirm():
    inputId = request.form['inputId']
    inputPassword = request.form['inputPassword']
    # CCTV 지역 리스트
    cctv_list = ['공대1,2호관','공대3호관','공대4호관','공대5호관']
    if (inputId=='admin'and inputPassword=='123'):
        session['username'] = inputId
        return render_template('map.html',cctv_list=cctv_list)
    else:
        return redirect(url_for('login'))

# 사용자 로그아웃
@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('login'))


# 카카오 토큰 및 텍스트 input
@app.route("/kakaotalk",methods=['POST'])
def kakaotalk():
    token = request.form['inputToken']
    text = request.form['inputText']
    kakao.sendToMeMessage(token, text)
    return redirect('kakaosend')

# 날씨 정보 불러오기
@app.route("/get_weather")
def weather():
    weather_list = job('전라남도 무안군 청계면')
    return render_template('detail.html', weather_list)

# 메인 페이지(지도)
@app.route('/map')
def map():
    if 'username' in session:
    # CCTV 지역 리스트
        cctv_list = ['공대1,2호관','공대3호관','공대4호관','공대5호관']
        return render_template('map.html',cctv_list=cctv_list)
    else:
        return redirect(url_for('login'))

# 대시보드
@app.route("/dashboard")
def dashboard():
    if 'username' in session:
    # CCTV 지역 리스트
        cctv_list = ['공대1,2호관','공대3호관','공대4호관','공대5호관']
        return render_template('dashboard.html',cctv_list=cctv_list)
    else:
        return redirect(url_for('login'))
    
# 이벤트로그
@app.route("/eventlog")
def eventlog():
    if 'username' in session:
    # CCTV 지역 리스트
        cctv_list = ['공대1,2호관','공대3호관','공대4호관','공대5호관']
        return render_template('eventlog.html',cctv_list=cctv_list)
    else:
        return redirect(url_for('login'))
    
# 프로파일
@app.route("/profile")
def profile():
    if 'username' in session:
        return render_template('profile.html')
    else:
        return redirect(url_for('login'))
    


#이벤트 발생시 드론화면
@app.route('/detail/drone_popup' ,methods=['GET', 'POST'])
def drone_popup():
    #창을 켰을 때 만 상태를 받아옴
    return render_template('drone_but.html')

def frame_generator(frame_base64):
    while True:
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_base64.encode() + b'\r\n')

@app.route('/drone_video', methods=['GET', 'POST'])
def drone_video():
    encoded_frame = request.data
    frame = cv2.imdecode(encoded_frame, cv2.IMREAD_COLOR)

    # 프레임을 비디오 태그에 인코딩합니다.
    encoded_frame = cv2.imencode('.jpg', frame)[1]

    # 프레임을 반환합니다.
    return encoded_frame

@app.route("/takeoff")
def takeoff():
  # 드론을 이륙시킵니다.
#   drone.takeoff()
    #@app.route("/")
    # def index():
    # # 다른 Flask 서버에 요청을 보냅니다.
    drone_url = "http://192.168.0.8:3000/takeoff"
    response = requests.get(drone_url)

  # 응답을 처리합니다.
    if response.status_code == 200:
        return "The other Flask server took off!"
    else:
        return "The other Flask server could not take off."

#   return "드론 이륙"

@app.route("/land")
def land():
  # 드론을 착륙시킵니다.
#   drone.land()
    print("Land")
#   return "드론 착륙"

@app.route("/droneStatus", methods=["GET"])
def droneStatus():
    conn = pymysql.connect(host='orion.mokpo.ac.kr',port = 8391, user='remote', password='1234', db='capstone', charset='utf8')
    cursor = conn.cursor()
    sql = '''select droneid, dronestate 
            from DRONE 
            WHERE droneid = 2 
            group by droneid, dronestate desc 
            limit 1;'''
    cursor.execute(sql)
    status_result = json.dumps(cursor.fetchall(), ensure_ascii=False)
    conn.close()

    return status_result

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000, threaded=True)
    
