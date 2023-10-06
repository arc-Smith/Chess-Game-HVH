#region imports
import os
from tkinter import Tk, Canvas, PhotoImage
import tkinter as tk
#endregion 

class Piece:
    def __init__(self, notation, color, pos_r, pos_c, legal_moves, defends):
        self.notation = notation
        self.color = color
        self.pos_r = pos_r
        self.pos_c = pos_c
        self.legal_moves = legal_moves
        self.defends = defends

class Queen(Piece):
    def __init__(self, notation, color, pos_r, pos_c, legal_moves, defends, check_pathway, pinned, pin_pathway):
        super().__init__(notation, color, pos_r, pos_c, legal_moves, defends)
        self.check_pathway = check_pathway
        self.pinned = pinned
        self.points = 9

class King(Piece):
    def __init__(self, notation, color, pos_r, pos_c, legal_moves, defends, moved, border, in_check):
        super().__init__(notation, color, pos_r, pos_c, legal_moves, defends)
        self.moved = moved
        self.border = border
        self.in_check = in_check

class Bishop(Piece):
    def __init__(self, notation, color, pos_r, pos_c, legal_moves, defends, check_pathway, pinned, pin_pathway):
        super().__init__(notation, color, pos_r, pos_c, legal_moves, defends)
        self.check_pathway = check_pathway
        self.pinned = pinned
        self.points = 3

class Knight(Piece):
    def __init__(self, notation, color, pos_r, pos_c, legal_moves, defends, pinned):
        super().__init__(notation, color, pos_r, pos_c, legal_moves, defends)
        self.pinned = pinned
        self.points = 3

class Rook(Piece):
    def __init__(self, notation, color, pos_r, pos_c, legal_moves, defends, moved, check_pathway, pinned, pin_pathway):
        super().__init__(notation, color, pos_r, pos_c, legal_moves, defends)
        self.moved = moved
        self.check_pathway = check_pathway
        self.pinned = pinned
        self.points = 5

class Pawn(Piece):
    def __init__(self, notation, color, pos_r, pos_c, legal_moves, defends, two_spaces, do_en_pass, get_en_pass, en_pass_count, pinned, pin_pathway):
        super().__init__(notation, color, pos_r, pos_c, legal_moves, defends)
        self.two_spaces = two_spaces
        self.do_en_pass = do_en_pass
        self.get_en_pass = get_en_pass
        self.en_pass_count = en_pass_count
        self.pinned = pinned
        self.points = 1

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