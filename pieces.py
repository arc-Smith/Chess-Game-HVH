# imports
import os
from tkinter import Tk, Canvas, PhotoImage
import tkinter as tk

class Piece:
    def __init__(self, notation, color, pos_r, pos_c, legal_moves, defends):
        self.notation = notation
        self.color = color
        self.pos_r = pos_r
        self.pos_c = pos_c
        self.legal_moves = legal_moves

class Queen(Piece):
    def __init__(self, notation, color, pos_r, pos_c, legal_moves, defends):
        super().__init__(notation, color, pos_r, pos_c, legal_moves)

class King(Piece):
    def __init__(self, notation, color, pos_r, pos_c, legal_moves, defends, moved):
        super().__init__(notation, color, pos_r, pos_c, legal_moves)
        self.moved = moved
    
    def castle(self):
        pass
    
    def check(self):
        pass
    
    def checkmate(self):
        pass

class Bishop(Piece):
    def __init__(self, notation, color, pos_r, pos_c, legal_moves, defends):
        super().__init__(notation, color, pos_r, pos_c, legal_moves)

class Knight(Piece):
    def __init__(self, notation, color, pos_r, pos_c, legal_moves, defends):
        super().__init__(notation, color, pos_r, pos_c, legal_moves)

class Rook(Piece):
    def __init__(self, notation, color, pos_r, pos_c, legal_moves, defends, moved):
        super().__init__(notation, color, pos_r, pos_c, legal_moves)
        self.moved = moved

class Pawn(Piece):
    def __init__(self, notation, color, pos_r, pos_c, legal_moves, defends, two_spaces, do_en_pass, get_en_pass, en_pass_count):
        super().__init__(notation, color, pos_r, pos_c, legal_moves)
        self.two_spaces = two_spaces
        self.do_en_pass = do_en_pass
        self.get_en_pass = get_en_pass
        self.en_pass_count = en_pass_count

    def promote(self):
        promotion_window = tk.Toplevel()
        promotion_window.title("Promote Pawn")
        promotion_window.geometry("300x150")

        if self.color == "white":
            radio_var = tk.StringVar()
            radio_var.set("Q") # automatically select white Queen

            label = tk.Label(promotion_window, text="Choose a piece to promote to:")
            label.pack()

            radio_queen = tk.Radiobutton(promotion_window, text="Queen", variable=radio_var, value="Q")
            radio_queen.pack()
            radio_rook = tk.Radiobutton(promotion_window, text="Rook", variable=radio_var, value="R")
            radio_rook.pack()
            radio_bishop = tk.Radiobutton(promotion_window, text="Bishop", variable=radio_var, value="B")
            radio_bishop.pack()
            radio_knight = tk.Radiobutton(promotion_window, text="Knight", variable=radio_var, value="N")
            radio_knight.pack()
    
        else:
            radio_var = tk.StringVar()
            radio_var.set("Qb") # automatically select black Queen

            label = tk.Label(promotion_window, text="Choose a piece to promote to:")
            label.pack()

            radio_queen = tk.Radiobutton(promotion_window, text="Queen", variable=radio_var, value="Qb")
            radio_queen.pack()
            radio_rook = tk.Radiobutton(promotion_window, text="Rook", variable=radio_var, value="Rb")
            radio_rook.pack()
            radio_bishop = tk.Radiobutton(promotion_window, text="Bishop", variable=radio_var, value="Bb")
            radio_bishop.pack()
            radio_knight = tk.Radiobutton(promotion_window, text="Knight", variable=radio_var, value="Nb")
            radio_knight.pack()

        # window is waiting for a selection to be made and confirmed with the destroying of the window 
        ok_button = tk.Button(promotion_window, text="Ok", command=promotion_window.destroy)
        ok_button.pack()

        promotion_window.wait_window()

        new_notation = radio_var.get()

        return new_notation