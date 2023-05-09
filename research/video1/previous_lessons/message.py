from tkinter import *
from PIL import ImageTk,Image
from tkinter import messagebox

root = Tk()
root.title('Learn To Code at Codemy.com')
root.iconbitmap('c:/gui/codemy.ico') #iconbitmap not quite working when I tried various things
root.geometry('400x400')

# showerror doesn't seem to work
def popup():
	response = messagebox.showinfo("This is my Popup!", "Hello World!")
	Label(root, text=response).pack()		
	#if response == "yes":
	#	Label(root, text="You Clicked Yes!").pack()
	#else:
	#	Label(root, text="You Clicked No!!").pack()

Button(root, text="Popup", command=popup).pack()

mainloop()
