from flask import Flask, render_template, Response, request, redirect
import cv2, camera, kakao

app = Flask(__name__)
camera1,camera2,camera3 = camera.camera_start()

# camera = cv2.VideoCapture('http://192.168.35.226:8000/stream.mjpg')
# camera1 = cv2.VideoCapture(0)
# camera2 = cv2.VideoCapture('http://192.168.35.226:8000/stream.mjpg')
# camera3 = cv2.VideoCapture(1)

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

@app.route('/video_feed/<string:cctv_section>')
def video_feed(cctv_section):
    if cctv_section=='남악1':
        return Response(gen_frames(camera1), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif cctv_section=='남악2':
        return Response(gen_frames(camera2), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif cctv_section=='목포대1':
        return Response(gen_frames(camera3), mimetype='multipart/x-mixed-replace; boundary=frame')
# CCTV상세정보
@app.route('/detail')
def detail():
    sec = request.args.get('section')
    return render_template('detail.html', sec=sec)
# 로그인페이지
@app.route('/')
def login():
    return render_template('login.html')
# 전체CCTV
@app.route('/all_cctv')
def all_cctv():
    cctv_list = ['남악1','남악2','목포대1','목포대2','하당1','하당2',]
    return render_template('all_cctv.html',cctv_list=cctv_list)

#카카오톡 보내기페이지
@app.route('/kakaosend')
def kakaosend():
    return render_template('kakao.html')

# 사용자 확인
@app.route("/kakaotalk",methods=['POST'])
def kakaotalk():
    token = request.form['inputToken']
    text = request.form['inputText']
    kakao.sendToMeMessage(token, text)
    return redirect('kakaosend')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000, threaded=True)
    
