# ------------------------------------------
# 웹기반 streamlit으로 실신자 분류 판별
# 실행 방법
# 터미널 창에 streamlit run app.py 입력
#-------------------------------------------
import streamlit as st
from PIL import Image
import io
import os
import pathlib
import shutil

import torch
model = torch.hub.load('ultralytics/yolov5', 'custom', 'best.pt')

st.title("Image Fall Detector")

st.write("> **쓰러짐 이미지 탐지 모델**")
uploaded_file = st.file_uploader('', type=['png', 'jpg'])
tmp_loc = False

if uploaded_file is not None:
    g = io.BytesIO(uploaded_file.read())
    tmp_loc = "result.png"
    
    with open(tmp_loc, 'wb') as out:
        out.write(g.read())
    out.close()
    
    img_local = Image.open(tmp_loc)
    _,c1, _ = st.columns(3)
    with c1:
        st.image(img_local, caption='')
        
        if st.button('탐지하기'):
            result=model([img_local])
            print(result.save())

            det_img = Image.open('./runs/detect/exp/result.jpg')
            st.image(det_img,caption='')


            shutil.rmtree('./runs')  
    os.remove(tmp_loc)




