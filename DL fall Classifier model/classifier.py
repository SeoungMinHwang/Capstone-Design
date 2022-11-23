from tkinter import *
from tkinter import filedialog
from os import path
from PIL import Image, ImageTk

width = 800
height = 600

x,y=300,200

win = Tk()

win.grid_columnconfigure(0, weight=1)
# win.configure(background="black")
win.title("Black Swan")
win.geometry(f'{width}x{height}')


Label(win, text="Fall Classifier", font=("맑은 고딕", 20, "bold")).grid(row=0, column=0)

def open_dialog():
    file = filedialog.askopenfilename(initialdir= path.dirname(__file__))    
    entered_file.delete(0, "end")
    entered_file.insert(0, file)
    
    # img = ImageTk.PhotoImage(file=Image.open(file, mode='r'))
    # canvas.create_image(x/2, y/2, image=img)

entered_file = Entry(win, width=50)
entered_file.grid(row=1, column=0)

button = Button(win, text="Upload", command=open_dialog)
button.grid(row=2, column=0)

py_img = PhotoImage(file="images/noimg.png")

label_img = Label(win, image=py_img)
label_img.grid(row=3, column=0)

# canvas.create_image(x/2, y/2, image=open_dialog())
# photo = PhotoImage(file="noimg.png")


win.mainloop()