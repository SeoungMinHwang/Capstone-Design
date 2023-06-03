from flask import Flask, render_template, Response, request, redirect, url_for,session
import cv2, camera, query, go_login, json
from weather_search import get_weather_daum, job
import json
import requests
# from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key='daemeolikkakkala'
camera1,camera2,camera3,camera4,camera5,camera6 = camera.camera_start()

cctv_list = query.cctv_list()
drone_list = query.drone_list()


# camera = cv2.VideoCapture('http://192.168.35.226:8000/stream.mjpg')
# camera1 = cv2.VideoCapture(0)
# camera2 = cv2.VideoCapture('http://192.168.35.226:8000/stream.mjpg')
# camera3 = cv2.VideoCapture(1)

# 영상 긁어오기
def gen_frames(camera):
    boundary = b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_data = buffer.tobytes()
            yield boundary + frame_data + b'\r\n--frame\r\n'

# 지역에 따른 response연결
@app.route('/video_feed/<string:cctv_section>')
def video_feed(cctv_section):
    if cctv_section==cctv_list[0]:
        return Response(gen_frames(camera1), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif cctv_section==cctv_list[1]:
        return Response(gen_frames(camera2), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif cctv_section==cctv_list[2]:
        return Response(gen_frames(camera3), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif cctv_section==cctv_list[3]:
        return Response(gen_frames(camera4), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif cctv_section==cctv_list[4]:
        return Response(gen_frames(camera5), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif cctv_section==cctv_list[5]:
        return Response(gen_frames(camera6), mimetype='multipart/x-mixed-replace; boundary=frame')

# CCTV상세정보
@app.route('/detail')
def detail():
    if 'username' in session:
        sec = request.args.get('section')
        place = query.detail_place(sec)
        return render_template('detail.html',sec=sec, place = place)
    else:
        return redirect(url_for('login'))
    
@app.route('/detail_get', methods = ['GET'])    
def detail_get():
    placename = request.args.get('placename')
    detail_list = query.detail_list(placename)
    result = json.dumps(detail_list)
    return result

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

@app.route('/drone_but')
def drone_but():
    return render_template('drone_but.html')

# 사용자 확인
@app.route("/login_confirm",methods=['POST'])
def login_confirm():
    inputId = request.form['inputId']
    inputPassword = request.form['inputPassword']
    # CCTV 지역 리스트
    idlist = query.get_idlist()
    if inputId in idlist:
        if (go_login.hash_password(inputPassword) == query.get_password(inputId)):
            map_list = query.map_list()
            session['username'] = inputId
            return render_template('map.html',cctv_list=cctv_list, map_list=map_list)
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

# 사용자 로그아웃
@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('login'))

# 날씨 정보 불러오기
@app.route("/get_weather")
def weather():
    weather_list = job('전라남도 무안군 청계면')
    return render_template('detail.html', weather_list)

# 메인 페이지(지도)
@app.route('/map')
def map():
    map_list = query.map_list()
    if 'username' in session:
    # CCTV 지역 리스트
        return render_template('map.html',cctv_list=cctv_list, map_list=map_list)
    else:
        return redirect(url_for('login'))

@app.route('/map_get', methods = ['GET'])    
def map_get():
    placename = request.args.get('placename')
    eventlist = query.event_list(placename)
    result = json.dumps(eventlist)
    return result

# 대시보드
@app.route("/dashboard")
def dashboard():
    day_per_eventlist = query.event_per_day()
    month_per_eventlist = query.event_per_month()
    place_per_eventlist = query.event_per_place()
    if 'username' in session:
    # CCTV 지역 리스트
        return render_template('dashboard.html',drone_list=drone_list,cctv_list=cctv_list, day_per_eventlist = day_per_eventlist, month_per_eventlist = month_per_eventlist, place_per_eventlist = place_per_eventlist)
    else:
        return redirect(url_for('login'))
    
# 이벤트로그
@app.route("/eventlog")
def eventlog():
    if 'username' in session:
    # CCTV 지역 리스트
        # cctv_list = ['공대1,2호관','공대3호관','공대4호관','공대5호관','대외협력관','스포츠센터']
        eventlist = query.show_event()
        return render_template('eventlog.html',cctv_list=cctv_list, eventlist = eventlist)
    else:
        return redirect(url_for('login'))
    
# 프로파일
@app.route("/profile")
def profile():
    if 'username' in session:
        userinfo = query.user_info(session['username'])
        print(userinfo)
        return render_template('profile.html', userinfo = userinfo)
    else:
        return redirect(url_for('login'))
    
#이벤트 발생시 드론화면
@app.route('/detail/drone_popup' ,methods=['GET', 'POST'])
def drone_popup():
    #창을 켰을 때 만 상태를 받아옴
    return render_template('drone_popup.html')

def frame_generator(frame_base64):
    while True:
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_base64.encode() + b'\r\n')

@app.route('/drone_video', methods=['GET', 'POST'])
def drone_video():
    response = requests.get('http://192.168.0.23:3000/take_video', stream=True)

  # 동영상 스트림을 읽습니다.
    while True:
        chunk = response.raw.read(1024)
        if not chunk:
            break

    # 동영상 스트림을 HTML에서 사용할 수 있게 리턴합니다.
    return chunk


@app.route("/takeoff")
def takeoff():
    drone_url = "http://192.168.0.23:3000/takeoff"
    response = requests.get(drone_url)

  # 응답을 처리합니다.
    if response.status_code == 200:
        return "The other Flask server took off!"
    else:
        return "The other Flask server could not take off."


@app.route("/land")
def land():
  # 드론을 착륙시킵니다.
#   drone.land()
    print("Land")
#   return "드론 착륙"

@app.route("/droneStatus", methods=["GET"])
def droneStatus():

    status_result = query.drone_state()

    return status_result

@app.route("/droneStatuslog", methods=["GET"])
def droneStatuslog():
    statuslog_result = query.droneStatus_log()
    
    return statuslog_result

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000, threaded=True)