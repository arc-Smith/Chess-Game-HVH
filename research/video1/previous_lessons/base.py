from tkinter import *
from PIL import ImageTk,Image

root = Tk()
root.title('Learn To Code at Codemy.com')

def open():
	global my_img
	top = Toplevel()
	top.title('My Second Window')
	my_img = ImageTk.PhotoImage(Image.open("images/cool1.png"))
	my_label = Label(top, image=my_img).pack()
	btn2 = Button(top, text="close window", command=top.destroy).pack()

btn = Button(root, text="Open Second Window", command=open).pack()

mainloop()
