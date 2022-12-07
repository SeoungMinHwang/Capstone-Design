# ------------------------------------------
# 웹기반 streamlit으로 실신자 분류기 판별
# 실행 방법
# 터미널 창에 streamlit run <파일이름> 입력
#-------------------------------------------
from fastai.vision.all import *
import streamlit as st
from PIL import Image
import io
import os
import pathlib
import subprocess

temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

learn_inf = load_learner('export.pkl')

def predict_info(img):
    pred, pred_idx, prob = learn_inf.predict(img)
    return (pred, prob[pred_idx])

st.title("Fall Classification")

st.write("> **이미지 분류 모델**")
uploaded_file = st.file_uploader('', type=['png', 'jpg'])
tmp_loc = False

if uploaded_file is not None:
    g = io.BytesIO(uploaded_file.read())
    tmp_loc = "result.png"
    
    with open(tmp_loc, 'wb') as out:
        out.write(g.read())
    out.close()

    image_local = Image.open(tmp_loc)
    _, c1, _ = st.columns(3)
    with c1:
        st.image(image_local, caption='')
        if st.button('분류하기'):
            pred, prob = predict_info(tmp_loc)
            st.success(f"분류: {pred}")
            st.success(f"확률: {(prob*100):0.2f}%")
            
            
    os.remove(tmp_loc)
