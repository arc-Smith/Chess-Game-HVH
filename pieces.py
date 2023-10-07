#region imports
import os
from tkinter import Tk, Canvas, PhotoImage
import tkinter as tk
#endregion 

class Piece:
    def __init__(self, notation, color, pos_r, pos_c, legal_moves, defends):
        self.notation = notation # white pieces have regular notation and black pieces have an added 'b' (ex. K for white king and Kb for black king)
        self.color = color
        self.pos_r = pos_r # connects to the row position (0-7) that the Piece is at on the board which is represented as a HashMap filled with squares
        self.pos_c = pos_c # connects to the column position (0-7) that the Piece is at on the board which is represented as a HashMap filled with squares
        self.legal_moves = legal_moves # array of positions that the piece can move to
        self.defends = defends # array holding positions (i.e. (r, c)) that contain a piece of the same color which is defended

class Queen(Piece):
    def __init__(self, notation, color, pos_r, pos_c, legal_moves, defends, check_pathway, pinned, pin_pathway):
        super().__init__(notation, color, pos_r, pos_c, legal_moves, defends)
        self.check_pathway = check_pathway # 
        self.pinned = pinned # true or false value indicating whether a piece is pinned
        self.pin_pathway = pin_pathway # array holding positions that the pinned piece can still move to (i.e. only squares that are inside of the pin pathway perhaps even taking its attacker)
        self.points = 9

class King(Piece):
    def __init__(self, notation, color, pos_r, pos_c, legal_moves, defends, moved, border, in_check):
        super().__init__(notation, color, pos_r, pos_c, legal_moves, defends)
        self.moved = moved # used to allow for castling with a Rook (if the King hasn't moved it can castle)
        self.border = border # used to disallow the kings from touching
        self.in_check = in_check # true or false value for the king being in check

class Bishop(Piece):
    def __init__(self, notation, color, pos_r, pos_c, legal_moves, defends, check_pathway, pinned, pin_pathway):
        super().__init__(notation, color, pos_r, pos_c, legal_moves, defends)
        self.check_pathway = check_pathway #
        self.pinned = pinned # true or false value indicating whether a piece is pinned
        self.pin_pathway = pin_pathway # array holding positions that the pinned piece can still move to (i.e. only squares that are inside of the pin pathway perhaps even taking its attacker)
        self.points = 3

class Knight(Piece):
    def __init__(self, notation, color, pos_r, pos_c, legal_moves, defends, pinned):
        super().__init__(notation, color, pos_r, pos_c, legal_moves, defends)
        self.pinned = pinned # true or false value indicating whether a piece is pinned
        self.points = 3

class Rook(Piece):
    def __init__(self, notation, color, pos_r, pos_c, legal_moves, defends, moved, check_pathway, pinned, pin_pathway):
        super().__init__(notation, color, pos_r, pos_c, legal_moves, defends)
        self.moved = moved # used to allow for castling with the King (if the Rook hasn't moved it can castle)
        self.check_pathway = check_pathway # 
        self.pinned = pinned # true or false value indicating whether a piece is pinned
        self.pin_pathway = pin_pathway # array holding positions that the pinned piece can still move to (i.e. only squares that are inside of the pin pathway perhaps even taking its attacker)
        self.points = 5

class Pawn(Piece):
    def __init__(self, notation, color, pos_r, pos_c, legal_moves, defends, two_spaces, do_en_pass, get_en_pass, en_pass_count, pinned, pin_pathway):
        super().__init__(notation, color, pos_r, pos_c, legal_moves, defends)
        self.two_spaces = two_spaces # used for moving 2 squares
        self.do_en_pass = do_en_pass # true or false value allowing a piece to en passant another
        self.get_en_pass = get_en_pass # true or false value allowing another piece en passant
        self.en_pass_count = en_pass_count # allows for en passant when the value is 1 meaning for 1 turn
        self.pinned = pinned # true or false value indicating whether a piece is pinned
        self.pin_pathway = pin_pathway # array holding positions that the pinned piece can still move to (i.e. only squares that are inside of the pin pathway perhaps even taking its attacker)
        self.points = 1

    def promote(self): # method for pawn promotion
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

        ok_button = tk.Button(promotion_window, text="Ok", command=promotion_window.destroy) # window is waiting for a selection to be made and confirmed from Ok
        ok_button.pack()

        promotion_window.wait_window()

        new_notation = radio_var.get()

        # if the window is simply closed then whichever piece is currently selected will be the promotion
        return new_notation