from flask import Flask, render_template, Response, request, redirect, url_for,session
import cv2, camera, kakao, query
from weather_search import get_weather_daum, job
# import requests
# from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key='daemeolikkakkala'
camera1,camera2,camera3,camera4,camera5,camera6 = camera.camera_start()

cctv_list = query.cctv_list()

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
        return render_template('detail.html',sec=sec)
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
        return render_template('map.html',cctv_list=cctv_list)
    else:
        return redirect(url_for('login'))

# 대시보드
@app.route("/dashboard")
def dashboard():
    if 'username' in session:
    # CCTV 지역 리스트
        return render_template('dashboard.html',cctv_list=cctv_list)
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
        return render_template('profile.html')
    else:
        return redirect(url_for('login'))
    


#카카오톡 보내기페이지
@app.route('/drone_popup')
def drone_popup():
    #창을 켰을 때 만 상태를 받아옴
    return render_template('drone_popup.html')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000, threaded=True)
    