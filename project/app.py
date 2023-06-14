from flask import Flask, render_template, Response, request, redirect, url_for,session, flash, jsonify
import cv2, camera, query, go_login, json
from weather_search import get_weather_daum, job
import json
import requests
from datetime import date
# from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key='daemeolikkakkala'
camera1,camera2,camera3,camera4,camera5,camera6 = camera.camera_start()

user_access = ""
log_cnt = len(query.event_log())
RUFirst = 0

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
    cctv_list = query.cctv_list()
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

# 전체CCTV
@app.route('/base')
def base():
    if 'username' in session:
    # CCTV 지역 리스트
        cctv_list = query.cctv_list()
        return render_template('base.html',user_access=user_access,cctv_list=cctv_list,log_cnt=log_cnt)
    else:
        return redirect(url_for('login'))
    
@app.route('/base_get')
def base_get():
    return str(len(query.event_log()))

@app.route('/base_cnt')
def base_cnt():
    place = query.last_event()
    global log_cnt
    log_cnt = len(query.event_log())
    return place

# CCTV상세정보
@app.route('/detail')
def detail():
    if 'username' in session:
        sec = request.args.get('section')
        place = query.detail_place(sec)
        return render_template('detail.html',log_cnt = log_cnt,user_access=user_access,sec=sec, place = place)
    else:
        return redirect(url_for('login'))
    
    # Detail Ajax
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
        cctv_list = query.cctv_list()
        return render_template('all_cctv.html',log_cnt = log_cnt,user_access=user_access,cctv_list=cctv_list)
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
    map_list = query.map_list()
    idlist = query.get_idlist()
    if inputId in idlist:
        if (go_login.hash_password(inputPassword) == query.get_password(inputId)):
            session['username'] = inputId
            global user_access
            global RUFirst
            RUFirst = 0
            user_access = query.user_access(session['username'])
            cctv_list = query.cctv_list()
            return render_template('map.html',user_access=user_access,cctv_list=cctv_list, map_list=map_list)
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

# 사용자 로그아웃
@app.route('/logout')
def logout():
    session.pop('username',None)
    global RUFirst
    RUFirst=0
    return redirect(url_for('login'))

# 날씨 정보 불러오기
@app.route("/get_weather")
def weather():
    weather_list = job('전라남도 무안군 청계면')
    return render_template('detail.html', weather_list)

# 메인 페이지(지도)
@app.route('/map')
def map():
    if 'username' in session:
        map_list = query.map_list()
    # CCTV 지역 리스트
        cctv_list = query.cctv_list()
        return render_template('map.html',user_access=user_access,cctv_list=cctv_list, map_list=map_list, log_cnt = log_cnt)
    else:
        return redirect(url_for('login'))

# AJAX용 map 테이블
@app.route('/map_get', methods = ['GET'])    
def map_get():
    placename = request.args.get('placename')
    eventlist = query.event_list(placename)
    result = json.dumps(eventlist)
    return result

# 로그인해서들어오면 확대
@app.route('/map_first', methods = ['GET'])    
def map_first():
    global RUFirst
    if RUFirst == 0:
        RUFirst = 1
        return jsonify(result=0)
    else:
        return jsonify(result=1)

# 대시보드
@app.route("/dashboard")
def dashboard():
    today = date.today()
    inputdate = today.strftime("%Y-%m-%d")
    day_per_eventlist = query.event_per_day()
    month_per_eventlist = query.event_per_month()
    place_per_eventlist = query.event_per_place()
    if 'username' in session:
    # CCTV 지역 리스트
        map_list = query.map_list()
        cctv_list = query.cctv_list()
        drone_list = query.drone_list()

        return render_template('dashboard.html',log_cnt = log_cnt,user_access=user_access,drone_list=drone_list,cctv_list=cctv_list, day_per_eventlist = day_per_eventlist, month_per_eventlist = month_per_eventlist, place_per_eventlist = place_per_eventlist, map_list=map_list, inputdate=inputdate)
    else:
        return redirect(url_for('login'))

# 대시보드 맵 날짜별 로 불러오기 ajax
@app.route("/dashboard_ajax", methods=['POST'])
def dashboard_ajax():
    inputdate = request.form['detectday']
    dayplace_per_eventlist = query.event_per_placeday_select(inputdate)
    response = jsonify(dayplace_per_eventlist)
    return response

# 이벤트로그
@app.route("/eventlog")
def eventlog():
    if 'username' in session:
    # CCTV 지역 리스트
        eventlist = query.show_event()
        eventlog_list = query.event_log()
        cctv_list = query.cctv_list()
        return render_template('eventlog.html',log_cnt = log_cnt,user_access=user_access,cctv_list=cctv_list, eventlist = eventlist, eventlog_list = eventlog_list)
    else:
        return redirect(url_for('login'))

# 프로파일
@app.route("/profile")
def profile():
    if 'username' in session:
        userinfo = query.user_info(session['username'])
        print(userinfo)
        return render_template('profile.html',log_cnt = log_cnt,user_access=user_access, userinfo = userinfo)
    else:
        return redirect(url_for('login'))

# CCTV추가
@app.route('/cctv_add')
def cctv_add():
    if 'username' in session:
        map_list = query.map_list()
        cctv_list = query.cctv_list()
        return render_template('cctv_add.html',log_cnt = log_cnt, user_access=user_access,cctv_list=cctv_list, map_list=map_list)
    else:
        return redirect(url_for('login'))
    
# CCTV추가 확인
@app.route("/cctv_add_confirm",methods=['POST'])
def cctv_add_confirm():
    map_list = query.map_list()
    cctv_list = query.cctv_list()
    flash('정상 등록 되었습니다.')
    clickLat = request.form['clickLat']
    clickLng = request.form['clickLng']
    inputAddress = request.form['inputAddress']
    inputPlacename = request.form['inputPlacename']
    inputPlacegruop = request.form['inputPlacegruop']
    inputIP = request.form['inputIP']
    inputWorking = request.form['inputWorking']
    if clickLat == "" and clickLng == "":
        flash('지도에서 위치를 클릭해주세요')
        return render_template('cctv_add.html', log_cnt = log_cnt, user_access=user_access,map_list=map_list)
    if inputPlacename in cctv_list:
        flash('장소가 중복됩니다. 수정해주세요.')
        return render_template('cctv_add.html', log_cnt = log_cnt, user_access=user_access,map_list=map_list)

    else:
        # cctv 추가하는 쿼리문 넣는곳
        query.cctv_insert(clickLat, clickLng, inputAddress, inputPlacename, inputPlacegruop, inputIP, inputWorking)
        map_list = query.map_list()
        cctv_list = query.cctv_list()
        return render_template('cctv_add.html',log_cnt = log_cnt, user_access=user_access, map_list=map_list)

# CCTV삭제
@app.route('/cctv_substract')
def cctv_substract():
    if 'username' in session:
        map_list = query.map_list()
        cctv_list = query.cctv_list()
        return render_template('cctv_substract.html',log_cnt = log_cnt, user_access=user_access,map_list=map_list)
    else:
        return redirect(url_for('login'))

# CCTV삭제 확인
@app.route("/cctv_substract_confirm",methods=['POST'])
def cctv_substract_confirm():
    flash('삭제완료 되었습니다.')
    # cctv 삭제 하는 쿼리문 넣는곳
    inputPlacename = request.form['inputPlacename']
    query.cctv_delete(inputPlacename)
    map_list = query.map_list()
    return render_template('cctv_substract.html',log_cnt = log_cnt, user_access=user_access,map_list=map_list)

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
    droneVd = cv2.VideoCapture('http://192.168.0.23:3000/take_video')
    return Response(gen_frames(droneVd), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/takeoff", methods=['GET', 'POST'])
def takeoff():
    dronenumber = request.form['number']  # Ajax 요청으로부터 전달된 번호 받기
    querydd=query.update_drone_state("go", dronenumber)

    return jsonify({'success': True})  # 성공 응답 반환


@app.route("/land", methods=['GET', 'POST'])
def land():
    dronenumber = request.form['number']  # Ajax 요청으로부터 전달된 번호 받기
    querydd=query.update_drone_state("back", dronenumber)

    return jsonify({'success': True})  # 성공 응답 반환

@app.route("/droneStatus", methods=["POST"])
def droneStatus():
    dronenumber = request.form['number']  # Ajax 요청으로부터 전달된 번호 받기       
    status_result = query.drone_state(dronenumber)

    return status_result

@app.route("/droneStatuslog", methods=["GET"])
def droneStatuslog():
    statuslog_result = query.droneStatus_log()
    
    return statuslog_result

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000, threaded=True)