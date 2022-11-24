from fastai.vision.all import *
import pathlib
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath
        
learn_inf = load_learner('export.pkl')

def predict_info(img_path):
    global learn_inf
    pred, pred_idx, probs = learn_inf.predict(img_path)
    
    return (pred, probs[pred_idx])
    
# print(predict_info('./images/fall_test2.jpg'))
    
# print(learn_inf.dls.vocab)
# 어떤 정보를 분류했는지 나옴

# <---ex--->
# print(learn_inf.predict('./images/fall_test.jpg'))
# pred: 예측된 범주(문자열)
# pred_idx : 에측된 범주의 색인 번호
# probs : 확률