# ------------------------------------------
# 웹기반 streamlit으로 실신자 분류 판별
# 실행 방법
# 터미널 창에 streamlit run app.py 입력
#-------------------------------------------
from fastai.vision.all import *
import streamlit as st
from PIL import Image
import io
import os
import pathlib

temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

learn_inf = load_learner('export.pkl')

def predict_info(img):
    pred, pred_idx, prob = learn_inf.predict(img)
    return (pred, prob[pred_idx])

st.title("Fall Classification")
st.sidebar.title("이미지 분류하기")
st.sidebar.write("## Fall Detection")

st.sidebar.write("한번 예측해보기 👋")
st.sidebar.write("**fall:쓰러짐 | notfallen:안쓰러짐**")
user_ans = st.sidebar.text_input("컴퓨터가 분류할 것 같은 것을 예측해보세요", value="", max_chars=20)

st.sidebar.write("**당신의 선택**:", user_ans)

st.write("> **컴퓨터는 이미지에 있는 사람이 쓰러졌다고 생각할까요 아니면 안쓰러졌다고 생각할까요**")
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
            
            if pred == user_ans:
                st.sidebar.success("예측성공")
            else:
                st.sidebar.error("예측실패")
                
    os.remove(tmp_loc)


# st.sidebar.write("**결과:**")