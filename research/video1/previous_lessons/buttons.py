from tkinter import *

root = Tk()

def myClick():
	myLabel = Label(root, text="Look! I clicked a Button!!")
	myLabel.pack()

# Make sure to not use parenthesis when putting the functions into the command
# bg doesn't work here on Mac
myButton = Button(root, text="Click Me!", command=myClick, bg="#000000", fg="red")
myButton.pack()

root.mainloop()
