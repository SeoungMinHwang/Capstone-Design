from flask import Flask, render_template, Response, request, redirect, url_for,session
import cv2, camera, kakao, pymysql

conn = pymysql.connect(host='127.0.0.1', user='root', password='7097', db='capstone', charset='utf8')
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
        return Response(gen_frames(camera1), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif cctv_section=='남악2':
        return Response(gen_frames(camera2), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif cctv_section=='목포대1':
        return Response(gen_frames(camera3), mimetype='multipart/x-mixed-replace; boundary=frame')
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
        return render_template('detail.html', eventlist = eventlist, responselist = responselist, dronelist = dronelist, sec=sec)
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
        cctv_list = ['남악1','남악2','목포대1','목포대2','하당1','하당2']
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

# 사용자 확인
@app.route("/login_confirm",methods=['POST'])
def login_confirm():
    inputId = request.form['inputId']
    inputPassword = request.form['inputPassword']
    if (inputId=='admin'and inputPassword=='123'):
        session['username'] = inputId
        return redirect(url_for('all_cctv'))
    else:
        return redirect(url_for('login'))

# 사용자 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# 카카오 토큰 및 텍스트 input
@app.route("/kakaotalk",methods=['POST'])
def kakaotalk():
    token = request.form['inputToken']
    text = request.form['inputText']
    kakao.sendToMeMessage(token, text)
    return redirect('kakaosend')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000, threaded=True)
    
