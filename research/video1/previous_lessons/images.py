from tkinter import *
from PIL import ImageTk,Image

root = Tk()
root.title('Learn To Code at Codemy.com')
root.iconbitmap('codemy.ico') #iconbitmap not quite working when I tried various things
root.geometry('500x500')

my_img = ImageTk.PhotoImage(Image.open("cool.png"))
my_label = Label(image=my_img)
my_label.pack()

button_quit = Button(root, text='Exit Program', command=root.quit)
button_quit.pack()

root.mainloop()
