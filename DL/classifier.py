from tkinter import *
from tkinter import filedialog
import os
from PIL import Image, ImageTk
import cv2

width = 500
height = 300

win = Tk()

win.grid_columnconfigure(0, weight=1)
# win.configure(background="black")
win.title("Black Swan")
win.geometry(f'{width}x{height}')


Label(win, text="Fall Classifier", font=("맑은 고딕", 20, "bold")).grid(row=0, column=0)

# print(__file__)
def open_dialog():
    global img
    
    file = filedialog.askopenfilename(initialdir="/")    
    entered_file.delete(0, "end")
    entered_file.insert(0, file)
    
    img = PhotoImage(file=file)
    label_img.config(image=img)

entered_file = Entry(win, width=50)
entered_file.grid(row=1, column=0)

button = Button(win, text="Upload", command=open_dialog)
button.grid(row=2, column=0) 

py_img = PhotoImage(file="./images/noimg.png", master=win)
label_img = Label(win, image=py_img)
label_img.grid(row=3, column=0)

win.mainloop()