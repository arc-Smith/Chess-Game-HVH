# from tkinter import *
# from PIL import ImageTk, Image
import os
from tkinter import Tk, Canvas, PhotoImage
import tkinter as tk

# chess pieces and chess board
w_pawn = os.path.join("designs", "white pieces", "white piece pngs", "white_pawn.png")
w_rook = os.path.join("designs", "white pieces", "white piece pngs", "white_rook.png")
w_knight = os.path.join("designs", "white pieces", "white piece pngs", "white_knight.png")
w_bishop = os.path.join("designs", "white pieces", "white piece pngs", "white_bishop.png")
w_queen = os.path.join("designs", "white pieces", "white piece pngs", "white_queen.png")
w_king = os.path.join("designs", "white pieces", "white piece pngs", "white_king.png")

b_pawn = os.path.join("designs", "black pieces", "black piece pngs", "black_pawn.png")
b_rook = os.path.join("designs", "black pieces", "black piece pngs", "black_rook.png")
b_knight = os.path.join("designs", "black pieces", "black piece pngs", "black_knight.png")
b_bishop = os.path.join("designs", "black pieces", "black piece pngs", "black_bishop.png")
b_queen = os.path.join("designs", "black pieces", "black piece pngs", "black_queen.png")
b_king = os.path.join("designs", "black pieces", "black piece pngs", "black_king.png")

w_board = os.path.join("designs", "chess boards", "whiteboard.png")
b_board = os.path.join("designs", "chess boards", "blackboard.png")

# classes and functions
def enter_fullscreen(event=None):
    root.attributes('-fullscreen', True)

def exit_fullscreen(event=None): 
    root.attributes("-fullscreen", False)
    root.geometry("1000x1000+{0}+{1}".format(int((root.winfo_screenwidth() - 1000)/2), int((root.winfo_screenheight() - 1000)/2)))

class ChessBoard(tk.Canvas):
    def __init__(self, parent, size):
        super().__init__(parent, width=size, height=size)
        self.size = size
        self.squares = {}
        self.piece_images = {
            "P": tk.PhotoImage(file=w_pawn),
            "R": tk.PhotoImage(file=w_rook),
            "N": tk.PhotoImage(file=w_knight),
            "B": tk.PhotoImage(file=w_bishop),
            "Q": tk.PhotoImage(file=w_queen),
            "K": tk.PhotoImage(file=w_king),
            "P2": tk.PhotoImage(file=b_pawn),
            "R2": tk.PhotoImage(file=b_rook),
            "N2": tk.PhotoImage(file=b_knight),
            "B2": tk.PhotoImage(file=b_bishop),
            "Q2": tk.PhotoImage(file=b_queen),
            "K2": tk.PhotoImage(file=b_king)
        }
        self.canvas = None
    
    def draw_board(self):
        canvas_width = 160
        canvas_height = 160
        canvas = Canvas(root, width=canvas_width, height=canvas_height, bg="black")
        canvas.pack()
        chessboard_img = PhotoImage(file=w_board)
        self.create_image(canvas_width//2, canvas_height//2, image=chessboard_img)
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col]
                if piece != "":
                    img = self.piece_images[piece]
                    self.canvas.create_image(col*self.square_size + self.square_size//2, row*self.square_size + self.square_size//2, image=img)

    def place_piece(self, piece, row, col):
        x, y = col * self.size // 8, row * self.size // 8
        image = self.piece_images[piece]
        self.create_image(x + self.size // 16, y + self.size // 16, image=image, anchor="nw")




# Establishes window in full screen with a title
root = Tk()
root.title('Terminal Chess Game Using Python')

board = ChessBoard(root, size=1000)
board.pack()
board.draw_board()
board.place_piece("K", 0, 4)
board.place_piece("K", 7, 4)

root.configure(bg="black")
enter_fullscreen()
root.bind("<Escape>", exit_fullscreen)

root.mainloop()