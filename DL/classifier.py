from tkinter import *
from tkinter import filedialog
import os
from PIL import Image, ImageTk
import cv2
from predict import predict_info
from tkinter import messagebox as msg

width = 550
height = 450
result_font = ("나눔 고딕", 13, "bold")

win = Tk()

win.grid_columnconfigure(0, weight=1)
win.configure(background="black")
win.title("BlackSwan")
win.geometry(f'{width}x{height}')
win.resizable(False, False)


Label(win, text="Fall Classifier", font=("맑은 고딕", 20, "bold"), fg='white', bg='black').grid(row=0, column=0, padx=5, pady=5)

def open_dialog():
    global img, pred, prob
    
    file = filedialog.askopenfilename(initialdir="/")    
    entered_file.delete(0, "end")
    entered_file.insert(0, file)

    
    img = Image.open(file).convert("RGB")
    img = img.resize((224, 224))
    path = "result.png"
    
    # tkinter 에서 .jpg 지원안하기 떄문에 .png로 변환 후 적용 
    # size를 변형했기때문에 어짜피 .png 로 변환안했어도 원본사진을 유지시킬려면 저장해야함
    img.save(path, 'png') # 현재 작업 경로에 저장
    img = PhotoImage(file=path)
    
    label_img.config(image=img)
    pred, prob = predict_info(path)
    
    # print(type(pred), type(prob))
    
    #  predic.config(text=pred)
    # proba.config(text=f'{(prob*100):0.2f}')
    os.remove('result.png')

def classifiy_btn():
    try:
        variableText1.set(pred)
        variableText2.set(f'{(prob*100):0.2f}')
    except:
        msg.showerror("경고","사진을 업로드 해주세요")

entered_file = Entry(win, width=55, bg='gray', justify="center")
entered_file.grid(row=1, column=0)

button = Button(win, text="Upload", command=open_dialog, bg="#464646", fg="white", cursor="hand2", font=("돋음", 10, "bold"))
button.grid(row=2, column=0, pady=(0,10)) 

py_img = PhotoImage(file="./images/noimg.png", master=win)
label_img = Label(win, image=py_img)
label_img.grid(row=3, column=0)

# 눌렀을떄 색상 바꾸기 : activebackground
classifier_btn = Button(win, text="Classifiy", width=15, bg="#464646", fg="white", font=("돋음",12,"bold"), cursor="hand2", command=classifiy_btn)
classifier_btn.grid(row=4, column=0)


result = Frame(win, bg="black")
result.grid(row=5, column=0, pady=10)
Label(result, text="Prediction", font=result_font, fg="white", bg="black").grid(row=0, column=0, padx=10)
Label(result, text="Probability", font=result_font, fg="white", bg="black").grid(row=0, column=1, padx=10)

ans = Frame(win, bg="black")
variableText1 = StringVar()
variableText2 = StringVar()
predic = Label(result, text="-", font=result_font, fg="#00A5FF", textvariable=variableText1, bg="black").grid(row=1, column=0, padx=10)
proba = Label(result, text="-", font=result_font, fg="#00A5FF", textvariable=variableText2, bg="black").grid(row=1, column=1, padx=10)


win.mainloop()