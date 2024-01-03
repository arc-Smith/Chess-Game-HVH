#region imports
import os
from tkinter import Tk, Canvas, PhotoImage, messagebox
import tkinter as tk
from pieces import Piece
from pieces import Pawn
from pieces import Rook
from pieces import Knight
from pieces import Bishop
from pieces import King
from pieces import Queen
import math
from collections import defaultdict
import copy
#endregion

#region chess piece images
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
#endregion

class ChessBoard(tk.Canvas):

    def __init__(self, parent, size):
        super().__init__(parent, width=size, height=size)
        self.size = size
        self.squares = {} # key=(row, column), value=[square id, piece or None, image id or None, color of square
        self.piece_images = {
            "P": tk.PhotoImage(file=w_pawn),
            "R": tk.PhotoImage(file=w_rook),
            "N": tk.PhotoImage(file=w_knight),
            "B": tk.PhotoImage(file=w_bishop),
            "Q": tk.PhotoImage(file=w_queen),
            "K": tk.PhotoImage(file=w_king),

            "Pb": tk.PhotoImage(file=b_pawn),
            "Rb": tk.PhotoImage(file=b_rook),
            "Nb": tk.PhotoImage(file=b_knight),
            "Bb": tk.PhotoImage(file=b_bishop),
            "Qb": tk.PhotoImage(file=b_queen),
            "Kb": tk.PhotoImage(file=b_king)
        }
        self.bind("<Button-1>", self.select_piece) # allows for a piece to be selected using left mouse click

        # self.clicked_r = None 
        # self.clicked_c = None
        self.clicked = None
        self.clicked_piece = None

        self.newClicked = None
        self.new_clicked_piece = None

        self.turn_based = ["white", "black"] # variable used to allow for turn based gameplay from white to black using mod operator and adding 1 to turns variable
        self.turns = 0

        # highlighting so it's clear whose turn it is
        self.greenHighlight = "#C9CC3F"	# Pear
        self.whiteHighlight = "#FFFAA0" # Pale Yellow
        self.fromTo = []

        # possible moves for each player after being put in check
        # self.white_possibles = {}
        # self.black_possibles = {}
        # Position of the piece mapped to the legal moves it can make to remove check
        self.incheck_move = defaultdict(list)
        self.incheck_take = defaultdict(list)
        self.incheck_interpose = defaultdict(list)
        self.checkers = [] # This is needed because having one or multiple pieces checking the King can impact whether all or one of moving, taking, or interposing is possible
        self.check_on_the_board = False

        # stalemate draw
        self.all_white_legal_moves = 20
        self.all_black_legal_moves = 20

        # insufficient material draw
        self.all_white_pieces = {}
        self.all_black_pieces = {}

        # 3-fold repetition
        self.game_states = []

        # fifty move rule
        self.fifty_move_rule = 0

    def create_board(self):
        square_size = self.size // 8 # each square will be 100x100
        white = "#eaebc8"
        green = "#638545"
        colors = [white, green] # two chosen chess board colors

        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2] # goes back and forth between the two chosen chess board colors
                x1, y1 = col * square_size, row * square_size 
                x2, y2 = x1 + square_size, y1 + square_size
                square = self.create_rectangle(x1, y1, x2, y2, fill=color, outline=color) # returns unique id for each square
                self.squares[(row, col)] = [square, None, None, color] # unique id entered into squares dictionary without a piece or image of a piece

    def place_piece(self, notation, color, row, col, legal_moves, defends, **kwargs):
        x, y = col * self.size // 8, row * self.size // 8
        image = self.piece_images[notation]

        # handling any additional attributes that pieces may have
        two_spaces = None
        do_en_pass = None
        get_en_pass = None
        en_pass_count = None
        moved = None
        border = None
        in_check = None
        check_pathway = None
        pinned = None
        pin_pathway = None

        for key, val in kwargs.items():
            if key == "two_spaces":
                two_spaces = val
            if key == "moved":
                moved = val
            if key == "do_en_pass":
                do_en_pass = val
            if key == "get_en_pass":
                get_en_pass = val
            if key == "en_pass_count":
                en_pass_count = val
            if key == "border":
                border = val
            if key == "in_check":
                in_check = val
            if key == "check_pathway":
                check_pathway = val
            if key == "pinned":
                pinned = val
            if key == "pin_pathway":
                pin_pathway = val

        if notation == "P":
            self.squares[(row, col)][1] = Pawn(notation, "white", row, col, legal_moves, defends, two_spaces, do_en_pass, get_en_pass, en_pass_count, pinned)
        elif notation == "Pb":
            self.squares[(row, col)][1] = Pawn(notation, "black", row, col, legal_moves, defends, two_spaces, do_en_pass, get_en_pass, en_pass_count, pinned)
        elif notation == "R":
            self.squares[(row, col)][1] = Rook(notation, "white", row, col, legal_moves, defends, moved, check_pathway, pinned, pin_pathway)
        elif notation == "Rb":
            self.squares[(row, col)][1] = Rook(notation, "black", row, col, legal_moves, defends, moved, check_pathway, pinned, pin_pathway)
        elif notation == "K":
            self.squares[(row, col)][1] = King(notation, "white", row, col, legal_moves, defends, moved, border, in_check)
        elif notation == "Kb":
            self.squares[(row, col)][1] = King(notation, "black", row, col, legal_moves, defends, moved, border, in_check)
        elif notation == "B":
            self.squares[(row, col)][1] = Bishop(notation, "white", row, col, legal_moves, defends, check_pathway, pinned, pin_pathway)
        elif notation == "Bb":
            self.squares[(row, col)][1] = Bishop(notation, "black", row, col, legal_moves, defends, check_pathway, pinned, pin_pathway)
        elif notation == "Q":
            self.squares[(row, col)][1] = Queen(notation, "white", row, col, legal_moves, defends, check_pathway, pinned, pin_pathway)
        elif notation == "Qb":
            self.squares[(row, col)][1] = Queen(notation, "black", row, col, legal_moves, defends, check_pathway, pinned, pin_pathway)
        elif notation == "N":
            self.squares[(row, col)][1] = Knight(notation, "white", row, col, legal_moves, defends, pinned)
        elif notation == "Nb":
            self.squares[(row, col)][1] = Knight(notation, "black", row, col, legal_moves, defends, pinned)

        # giving the square a unique image id to be used when moving pieces or removing pieces
        self.squares[(row, col)][2] = self.create_image(x, y, image=image, anchor="nw")

    def select_piece(self, event):  
        # finding the selected square
        r = 0
        c = 0
        for col in range(1,9):
            if (event.x <= col*100 and event.x >= (col-1)*100):
                c = col-1
        for row in range(1,9):
            if (event.y <= row*100 and event.y >= (row-1)*100):
                r = row-1

        clicked_row = r
        clicked_col = c
        square_id = self.squares[(r, c)][0]
        self.clicked_piece = self.squares[(r, c)][1] 
        
        # if check is on the board but it's not checkmate then something must be done about that
        if self.check_on_the_board:
            if self.clicked_piece != None and self.clicked_piece.color == self.turn_based[self.turns % 2]:
                    if (r, c) in self.incheck_move or (r, c) in self.incheck_take or (r, c) in self.incheck_interpose:
                        if len(self.clicked_piece.legal_moves) >= 1:
                            highlight = self.whiteHighlight if self.squares[(clicked_row, clicked_col)][3] == "#eaebc8" else self.greenHighlight
                            self.turns += 1
                            self.itemconfigure(square_id, fill=highlight, outline=highlight, width=0)
                            self.update()
                            self.clicked = square_id

                            # taking into account the turns that have occurred for any pawns granted en passant
                            for key, val in self.squares.items():
                                if val[1] != None and (val[1].notation == "P" or val[1].notation == "Pb"):
                                    if val[1].do_en_pass == True or val[1].get_en_pass:
                                        val[1].en_pass_count += 1 # changing the en_pass_count from 0 to 1 so that it can be set to False in the move_piece function

                            self.bind("<Button-1>", lambda e: self.move_piece(e, r, c, square_id, self.clicked_piece))
        else:
            # if a square was selected already and the new square has a piece - not sure anymore what purpose is here
            # if self.clicked != None and self.squares[(r, c)][1] != None:
            #     self.itemconfigure(self.clicked, fill=self.squares[(r, c)][3], outline=self.squares[(r, c)][3], width=0)
            #     self.update()
            #     self.clicked = None
            # else:
                # making sure only one square that has a piece and legal moves can be selected at a time
                # also goes back and forth between the white and black pieces
            if self.clicked_piece != None and self.clicked_piece.legal_moves != [] and self.clicked_piece.color == self.turn_based[self.turns % 2]:
                if self.clicked_piece.legal_moves != None:
                    # if self.clicked_piece.notation != "K" and self.clicked_piece.notation != "Kb":
                    #     pass
                    if len(self.clicked_piece.legal_moves) >= 1:
                            highlight = self.whiteHighlight if self.squares[(clicked_row, clicked_col)][3] == "#eaebc8" else self.greenHighlight
                            self.turns += 1
                            self.itemconfigure(square_id, fill=highlight, outline=highlight, width=0)
                            self.update()
                            self.clicked = square_id

                            # taking into account the turns that have occurred for any pawns granted en passant
                            for key, val in self.squares.items():
                                if val[1] != None and (val[1].notation == "P" or val[1].notation == "Pb"):
                                    if val[1].do_en_pass == True or val[1].get_en_pass:
                                        val[1].en_pass_count += 1 # changing the en_pass_count from 0 to 1 so that it can be set to False in the move_piece function

                            self.bind("<Button-1>", lambda e: self.move_piece(e, r, c, square_id, self.clicked_piece))
    
    def move_piece(self, event, from_square_r, from_square_c, from_square_id, actual_piece):        
        # finding the row and col of the next selected square
        r = 0
        c = 0
        for col in range(1,9):
            if (event.x <= col*100 and event.x >= (col-1)*100):
                c = col-1
        for row in range(1,9):
            if (event.y <= row*100 and event.y >= (row-1)*100):
                r = row-1

        # coordinates that selected piece may move to
        move_to = (r, c)

        # loop to get a legal coordinate selection
        if self.check_on_the_board:
            removeCheck = []
            for row,col in actual_piece.legal_moves:
                if (actual_piece.pos_r, actual_piece.pos_c) in self.incheck_move and (row, col) in self.incheck_move[(actual_piece.pos_r, actual_piece.pos_c)]:
                    removeCheck.append((row, col))
                if (actual_piece.pos_r, actual_piece.pos_c) in self.incheck_take and (row, col) in self.incheck_take[(actual_piece.pos_r, actual_piece.pos_c)]:
                    removeCheck.append((row, col))
                if (actual_piece.pos_r, actual_piece.pos_c) in self.incheck_interpose and (row, col) in self.incheck_interpose[(actual_piece.pos_r, actual_piece.pos_c)]:
                    removeCheck.append((row, col))
            if move_to not in removeCheck:
                print("you can't get out of check that way")
                print("horrid cord - " + str(move_to))
                print("The cord is no good")
                print("w moves = "+str(removeCheck))
                print("\n")
                self.bind("<Button-1>", lambda e: self.move_piece(e, from_square_r, from_square_c, from_square_id, actual_piece))
                return
            else:
                self.incheck_move = defaultdict(list)
                self.incheck_take = defaultdict(list)
                self.incheck_interpose = defaultdict(list)
                self.checkers = [] # This is needed because having one or multiple pieces checking the King can impact whether all or one of moving, taking, or interposing is possible
                self.check_on_the_board = False
                # setting self.in_check to false for both kings
                for key, val in self.squares.items():
                    if val[1] != None:
                        if val[1].notation == "K" or val[1].notation == "Kb":
                            val[1].in_check = False
        elif (move_to not in actual_piece.legal_moves):
            print("YOU SHALL NOT PASS")
            print("BAD COORDINATE - " + str(move_to))
            print("The coordinate is simply invalid")
            print("Legal moves = "+str(actual_piece.legal_moves))
            print("\n")
            self.bind("<Button-1>", lambda e: self.move_piece(e, from_square_r, from_square_c, from_square_id, actual_piece))
            return
        
        self.fifty_move_rule += 1

        #region KING move piece
        if actual_piece.notation == "K" or actual_piece.notation == "Kb":
            # removing the piece's existence then its image from prior square
            self.squares[(from_square_r, from_square_c)][1] = None
            root.after(0000, self.delete, self.squares[(from_square_r, from_square_c)][2])
            self.squares[(from_square_r, from_square_c)][2] = None
           
            # TAKING A PIECE
            if (self.squares[(r,c)][1] != None):
                # removing the piece if it has been eaten by King
                self.squares[(r, c)][1] = None
                root.after(0000, self.delete, self.squares[(r, c)][2])
                self.squares[(r, c)][2] = None
                self.fifty_move_rule = 0

            # find the next legal moves for this piece
            add_legal_moves = self.get_legal_moves(actual_piece, r, c)

            # placing the piece onto a new square with its image
            self.place_piece(actual_piece.notation, actual_piece.color, r, c, add_legal_moves, actual_piece.defends, moved=True, border=actual_piece.border)

            # DESELECTION / no more outline
            # self.itemconfigure(self.clicked, fill=self.squares[(from_square_r, from_square_c)][3], outline=self.squares[(from_square_r, from_square_c)][3], width=0)
            # self.update()
            # self.clicked = None

            # HIGHLIGHT / highlight past position
            highlight = self.whiteHighlight if self.squares[(from_square_r, from_square_c)][3] == "#eaebc8" else self.greenHighlight
            self.itemconfigure(self.clicked, fill=highlight, outline=highlight, width=0)
            self.update()
            self.clicked = None
            self.fromTo.append([from_square_r, from_square_c])

            # Removing enemy piece highlight
            self.highlighting()

            # HIGHLIGHT / highlight new position
            self.newClicked = self.squares[(r, c)][0]
            highlight = self.whiteHighlight if self.squares[(r, c)][3] == "#eaebc8" else self.greenHighlight
            self.itemconfigure(self.newClicked, fill=highlight, outline=highlight, width=0)
            self.update()
            self.newClicked = None
            self.fromTo.append([r, c])

            # black king CASTLE queen side
            if (actual_piece.notation == "Kb") and actual_piece.moved == False:
                if ((r,c) == (0,2)):
                    the_rook = self.squares[(0,0)][1]

                    # removing the rook's existence then its image from prior square
                    self.squares[(0, 0)][1] = None
                    root.after(0000, self.delete, self.squares[(0, 0)][2])
                    self.squares[(0, 0)][2] = None
                
                    # find the next legal moves for this piece
                    add_legal_moves = self.get_legal_moves(the_rook, 0, 3)

                    # placing the piece onto a new square with its image
                    self.place_piece(the_rook.notation, the_rook.color, 0, 3, add_legal_moves, the_rook.defends, moved=True)
            
            # black king CASTLE king side
            if (actual_piece.notation == "Kb") and actual_piece.moved == False:
                if ((r,c) == (0,6)):
                    the_rook = self.squares[(0,7)][1]

                    # removing the rook's existence then its image from prior square
                    self.squares[(0, 7)][1] = None
                    root.after(0000, self.delete, self.squares[(0, 7)][2])
                    self.squares[(0, 7)][2] = None
                
                    # find the next legal moves for this piece
                    add_legal_moves = self.get_legal_moves(the_rook, 0, 5)

                    # placing the piece onto a new square with its image
                    self.place_piece(the_rook.notation, the_rook.color, 0, 5, add_legal_moves, the_rook.defends, moved=True)
            
            # white king CASTLE queen side
            if (actual_piece.notation == "K") and actual_piece.moved == False:
                if ((r,c) == (7,2)):
                    the_rook = self.squares[(7,0)][1]

                    # removing the rook's existence then its image from prior square
                    self.squares[(7, 0)][1] = None
                    root.after(0000, self.delete, self.squares[(7, 0)][2])
                    self.squares[(7, 0)][2] = None
                
                    # find the next legal moves for this piece
                    add_legal_moves = self.get_legal_moves(the_rook, 7, 3)

                    # placing the piece onto a new square with its image
                    self.place_piece(the_rook.notation, the_rook.color, 7, 3, add_legal_moves, the_rook.defends, moved=True)
            
            # white king CASTLE king side
            if (actual_piece.notation == "K") and actual_piece.moved == False:
                if ((r,c) == (7,6)):
                    the_rook = self.squares[(7,7)][1]

                    # removing the rook's existence then its image from prior square
                    self.squares[(7, 7)][1] = None
                    root.after(0000, self.delete, self.squares[(7, 7)][2])
                    self.squares[(7, 7)][2] = None
                
                    # find the next legal moves for this piece
                    add_legal_moves = self.get_legal_moves(the_rook, 7, 5)

                    # placing the piece onto a new square with its image
                    self.place_piece(the_rook.notation, the_rook.color, 7, 5, add_legal_moves, the_rook.defends, moved=True)

            # putting the next left click back onto the select_piece function
            self.bind("<Button-1>", self.select_piece)

            # make sure all pieces have their correct legal moves
            for key, val in self.squares.items():
                if val[1] != None:
                    val[1].legal_moves = self.get_legal_moves(val[1], val[1].pos_r, val[1].pos_c)
        #endregion

        #region QUEEN move piece
        if actual_piece.notation == "Q" or actual_piece.notation == "Qb":
            # removing the piece's existence then its image from prior square
            self.squares[(from_square_r, from_square_c)][1] = None
            root.after(0000, self.delete, self.squares[(from_square_r, from_square_c)][2])
            self.squares[(from_square_r, from_square_c)][2] = None
           
            # TAKING A PIECE
            if (self.squares[(r,c)][1] != None):
                # removing the piece if it has been eaten by Queen
                self.squares[(r, c)][1] = None
                root.after(0000, self.delete, self.squares[(r, c)][2])
                self.squares[(r, c)][2] = None
                self.fifty_move_rule = 0

            # find the next legal moves for this piece
            add_legal_moves = self.get_legal_moves(actual_piece, r, c)

            # placing the piece onto a new square with its image
            self.place_piece(actual_piece.notation, actual_piece.color, r, c, add_legal_moves, actual_piece.defends)

            # DESELECTION / no more outline
            # self.itemconfigure(self.clicked, fill=self.squares[(from_square_r, from_square_c)][3], outline=self.squares[(from_square_r, from_square_c)][3], width=0)
            # self.update()
            # self.clicked = None

            # HIGHLIGHT / highlight past position
            highlight = self.whiteHighlight if self.squares[(from_square_r, from_square_c)][3] == "#eaebc8" else self.greenHighlight
            self.itemconfigure(self.clicked, fill=highlight, outline=highlight, width=0)
            self.update()
            self.clicked = None
            self.fromTo.append([from_square_r, from_square_c])

            # Removing enemy piece highlight
            self.highlighting()

            # HIGHLIGHT / highlight new position
            self.newClicked = self.squares[(r, c)][0]
            highlight = self.whiteHighlight if self.squares[(r, c)][3] == "#eaebc8" else self.greenHighlight
            self.itemconfigure(self.newClicked, fill=highlight, outline=highlight, width=0)
            self.update()
            self.newClicked = None
            self.fromTo.append([r, c])

            # putting the next left click back onto the select_piece function
            self.bind("<Button-1>", self.select_piece)

            # make sure all pieces have their correct legal moves
            for key, val in self.squares.items():
                if val[1] != None:
                    val[1].legal_moves = self.get_legal_moves(val[1], val[1].pos_r, val[1].pos_c)
        #endregion

        #region BISHOP move piece
        if actual_piece.notation == "B" or actual_piece.notation == "Bb":
            # removing the piece's existence then its image from prior square
            self.squares[(from_square_r, from_square_c)][1] = None
            root.after(0000, self.delete, self.squares[(from_square_r, from_square_c)][2])
            self.squares[(from_square_r, from_square_c)][2] = None

            # TAKING A PIECE
            if (self.squares[(r,c)][1] != None):
                # removing the piece if it has been eaten by Bishop
                self.squares[(r, c)][1] = None
                root.after(0000, self.delete, self.squares[(r, c)][2])
                self.squares[(r, c)][2] = None
                self.fifty_move_rule = 0

            # find the next legal moves for this piece
            add_legal_moves = self.get_legal_moves(actual_piece, r, c)

            # placing the piece onto a new square with its image
            self.place_piece(actual_piece.notation, actual_piece.color, r, c, add_legal_moves, actual_piece.defends)

            # DESELECTION / no more outline
            # self.itemconfigure(self.clicked, fill=self.squares[(from_square_r, from_square_c)][3], outline=self.squares[(from_square_r, from_square_c)][3], width=0)
            # self.update()
            # self.clicked = None

            # HIGHLIGHT / highlight past position
            highlight = self.whiteHighlight if self.squares[(from_square_r, from_square_c)][3] == "#eaebc8" else self.greenHighlight
            self.itemconfigure(self.clicked, fill=highlight, outline=highlight, width=0)
            self.update()
            self.clicked = None
            self.fromTo.append([from_square_r, from_square_c])

            # Removing enemy piece highlight
            self.highlighting()

            # HIGHLIGHT / highlight new position
            self.newClicked = self.squares[(r, c)][0]
            highlight = self.whiteHighlight if self.squares[(r, c)][3] == "#eaebc8" else self.greenHighlight
            self.itemconfigure(self.newClicked, fill=highlight, outline=highlight, width=0)
            self.update()
            self.newClicked = None
            self.fromTo.append([r, c])

            # putting the next left click back onto the select_piece function
            self.bind("<Button-1>", self.select_piece)

            # make sure all pieces have their correct legal moves
            for key, val in self.squares.items():
                if val[1] != None:
                    val[1].legal_moves = self.get_legal_moves(val[1], val[1].pos_r, val[1].pos_c)
        #endregion

        #region KNIGHT move piece
        if actual_piece.notation == "N" or actual_piece.notation == "Nb":
            # removing the piece's existence then its image from prior square
            self.squares[(from_square_r, from_square_c)][1] = None
            root.after(0000, self.delete, self.squares[(from_square_r, from_square_c)][2])
            self.squares[(from_square_r, from_square_c)][2] = None

            # TAKING A PIECE
            if (self.squares[(r,c)][1] != None):
                # removing the piece if it has been eaten by Rook
                self.squares[(r, c)][1] = None
                root.after(0000, self.delete, self.squares[(r, c)][2])
                self.squares[(r, c)][2] = None
                self.fifty_move_rule = 0

            # find the next legal moves for this piece
            add_legal_moves = self.get_legal_moves(actual_piece, r, c)

            # placing the piece onto a new square with its image
            self.place_piece(actual_piece.notation, actual_piece.color, r, c, add_legal_moves, actual_piece.defends)

            # DESELECTION / no more outline
            # self.itemconfigure(self.clicked, fill=self.squares[(from_square_r, from_square_c)][3], outline=self.squares[(from_square_r, from_square_c)][3], width=0)
            # self.update()
            # self.clicked = None

            # HIGHLIGHT / highlight past position
            highlight = self.whiteHighlight if self.squares[(from_square_r, from_square_c)][3] == "#eaebc8" else self.greenHighlight
            self.itemconfigure(self.clicked, fill=highlight, outline=highlight, width=0)
            self.update()
            self.clicked = None
            self.fromTo.append([from_square_r, from_square_c])

            # Removing enemy piece highlight
            self.highlighting()

            # HIGHLIGHT / highlight new position
            self.newClicked = self.squares[(r, c)][0]
            highlight = self.whiteHighlight if self.squares[(r, c)][3] == "#eaebc8" else self.greenHighlight
            self.itemconfigure(self.newClicked, fill=highlight, outline=highlight, width=0)
            self.update()
            self.newClicked = None
            self.fromTo.append([r, c])

            # putting the next left click back onto the select_piece function
            self.bind("<Button-1>", self.select_piece)

            # make sure all pieces have their correct legal moves
            for key, val in self.squares.items():
                if val[1] != None:
                    val[1].legal_moves = self.get_legal_moves(val[1], val[1].pos_r, val[1].pos_c)
        #endregion

        #region ROOK move piece
        if actual_piece.notation == "R" or actual_piece.notation == "Rb":
            # removing the piece's existence then its image from prior square
            self.squares[(from_square_r, from_square_c)][1] = None
            root.after(0000, self.delete, self.squares[(from_square_r, from_square_c)][2])
            self.squares[(from_square_r, from_square_c)][2] = None

            # TAKING A PIECE
            if (self.squares[(r,c)][1] != None):
                # removing the piece if it has been eaten by Rook
                self.squares[(r, c)][1] = None
                root.after(0000, self.delete, self.squares[(r, c)][2])
                self.squares[(r, c)][2] = None
                self.fifty_move_rule = 0

            # find the next legal moves for this piece
            add_legal_moves = self.get_legal_moves(actual_piece, r, c)

            # placing the piece onto a new square with its image
            self.place_piece(actual_piece.notation, actual_piece.color, r, c, add_legal_moves, actual_piece.defends, moved=True)

            # DESELECTION / no more outline
            # self.itemconfigure(self.clicked, fill=self.squares[(from_square_r, from_square_c)][3], outline=self.squares[(from_square_r, from_square_c)][3], width=0)
            # self.update()
            # self.clicked = None

            # HIGHLIGHT / highlight past position
            highlight = self.whiteHighlight if self.squares[(from_square_r, from_square_c)][3] == "#eaebc8" else self.greenHighlight
            self.itemconfigure(self.clicked, fill=highlight, outline=highlight, width=0)
            self.update()
            self.clicked = None
            self.fromTo.append([from_square_r, from_square_c])

            # Removing enemy piece highlight
            self.highlighting()

            # HIGHLIGHT / highlight new position
            self.newClicked = self.squares[(r, c)][0]
            highlight = self.whiteHighlight if self.squares[(r, c)][3] == "#eaebc8" else self.greenHighlight
            self.itemconfigure(self.newClicked, fill=highlight, outline=highlight, width=0)
            self.update()
            self.newClicked = None
            self.fromTo.append([r, c])

            # putting the next left click back onto the select_piece function
            self.bind("<Button-1>", self.select_piece)

            # make sure all pieces have their correct legal moves
            for key, val in self.squares.items():
                if val[1] != None:
                    val[1].legal_moves = self.get_legal_moves(val[1], val[1].pos_r, val[1].pos_c)
        #endregion

        #region PAWN move piece
        if actual_piece.notation == "P" or actual_piece.notation == "Pb":
            # removing the piece's existence then its image from prior square
            self.squares[(from_square_r, from_square_c)][1] = None
            root.after(0000, self.delete, self.squares[(from_square_r, from_square_c)][2])
            self.squares[(from_square_r, from_square_c)][2] = None

            # TAKING A PIECE
            if (self.squares[(r,c)][1] != None):
                # removing the piece if it has been taken by Pawn
                self.squares[(r, c)][1] = None
                root.after(0000, self.delete, self.squares[(r, c)][2])
                self.squares[(r, c)][2] = None
                self.fifty_move_rule = 0
            elif (self.squares[(r,c)][1] == None) and (self.squares[(r+1,c)][1] != None) and (self.squares[(r+1,c)][1].notation == "Pb") and (actual_piece.notation == "P") and (actual_piece.do_en_pass == True) and (self.squares[(r+1,c)][1].get_en_pass == True):
                # removing the piece if it has been en passant-ed by White Pawn
                print("REMOVING the BLACK pawn to the left/right of WHITE pawn")
                print(f"BLACK pawn to be removed is at ({r+1},{c})\n")
                self.squares[(r+1, c)][1] = None
                root.after(0000, self.delete, self.squares[(r+1, c)][2])
                self.squares[(r+1, c)][2] = None
                self.fifty_move_rule = 0
            elif (self.squares[(r,c)][1] == None) and (self.squares[(r-1,c)][1] != None) and (self.squares[(r-1,c)][1].notation == "P") and (actual_piece.notation == "Pb") and (actual_piece.do_en_pass == True) and (self.squares[(r-1,c)][1].get_en_pass == True):
                # removing the piece if it has been en passant-ed by Black Pawn
                print("REMOVING the WHITE pawn to the left/right of BLACK pawn")
                print(f"WHITE pawn to be removed is at ({r-1},{c})\n")
                self.squares[(r-1, c)][1] = None
                root.after(0000, self.delete, self.squares[(r-1, c)][2])
                self.squares[(r-1, c)][2] = None
                self.fifty_move_rule = 0

            # en passant given to enemy piece that's on left of white pawn
            if (c >= 1):
                if (r==(from_square_r-2)) and (actual_piece.two_spaces == True) and (actual_piece.notation == "P") and (self.squares[(r,c-1)][1] != None) and (self.squares[(r,c-1)][1].color != actual_piece.color):
                    self.squares[(r,c-1)][1].do_en_pass = True
                    actual_piece.get_en_pass = True
            # en passant given to enemy piece that's on right of white pawn
            if (c <= 6):
                if (r==(from_square_r-2)) and (actual_piece.two_spaces == True) and (actual_piece.notation == "P") and (self.squares[(r,c+1)][1] != None) and (self.squares[(r,c+1)][1].color != actual_piece.color):
                    self.squares[(r,c+1)][1].do_en_pass = True
                    actual_piece.get_en_pass = True  
            # en passant given to enemy piece that's on left of black pawn
            if (c >= 1):
                if (r==(from_square_r+2)) and (actual_piece.two_spaces == True) and (actual_piece.notation == "Pb") and (self.squares[(r,c-1)][1] != None) and (self.squares[(r,c-1)][1].color != actual_piece.color):
                    self.squares[(r,c-1)][1].do_en_pass = True
                    actual_piece.get_en_pass = True
            # en passant given to enemy piece that's on right of black pawn
            if (c <= 6):
                if (r==(from_square_r+2)) and (actual_piece.two_spaces == True) and (actual_piece.notation == "Pb") and (self.squares[(r,c+1)][1] != None) and (self.squares[(r,c+1)][1].color != actual_piece.color):
                    self.squares[(r,c+1)][1].do_en_pass = True
                    actual_piece.get_en_pass = True

            # promoting pawn to a selected piece
            new_notation = None
            if r==0 and actual_piece.notation == "P":
                new_notation = actual_piece.promote()
                actual_piece.notation = new_notation
            elif r==7 and actual_piece.notation == "Pb":
                new_notation = actual_piece.promote()
                actual_piece.notation = new_notation
            

            # find the next legal moves for this piece
            add_legal_moves = self.get_legal_moves(actual_piece, r, c)

            # placing the piece onto a new square with its image
            self.place_piece(actual_piece.notation, actual_piece.color, r, c, add_legal_moves, actual_piece.defends, two_spaces=False, do_en_pass=actual_piece.do_en_pass, get_en_pass=actual_piece.get_en_pass, en_pass_count=actual_piece.en_pass_count)

            # DESELECTION / no more outline
            # self.itemconfigure(self.clicked, fill=self.squares[(from_square_r, from_square_c)][3], outline=self.squares[(from_square_r, from_square_c)][3], width=0)
            # self.update()
            # self.clicked = None
            # self.fromTo.append([from_square_r, from_square_c])

            # HIGHLIGHT / highlight past position
            highlight = self.whiteHighlight if self.squares[(from_square_r, from_square_c)][3] == "#eaebc8" else self.greenHighlight
            self.itemconfigure(self.clicked, fill=highlight, outline=highlight, width=0)
            self.update()
            self.clicked = None
            self.fromTo.append([from_square_r, from_square_c])

            # Removing enemy piece highlight
            self.highlighting()

            # HIGHLIGHT / highlight new position
            self.newClicked = self.squares[(r, c)][0]
            highlight = self.whiteHighlight if self.squares[(r, c)][3] == "#eaebc8" else self.greenHighlight
            self.itemconfigure(self.newClicked, fill=highlight, outline=highlight, width=0)
            self.update()
            self.newClicked = None
            self.fromTo.append([r, c])

            # putting the next left click back onto the select_piece function
            self.bind("<Button-1>", self.select_piece)

            # make sure all pieces have their correct legal moves
            for key, val in self.squares.items():
                if val[1] != None:
                    val[1].legal_moves = self.get_legal_moves(val[1], val[1].pos_r, val[1].pos_c)
            
            self.fifty_move_rule = 0
        #endregion
        self.en_passant()
        self.pinsChecksCheckmate()
        self.draws()
    
    def highlighting(self):
        if len(self.fromTo) > 2:
                r,c = self.fromTo.pop(0)
                self.itemconfigure(self.squares[(r, c)][0], fill=self.squares[(r, c)][3], outline=self.squares[(r, c)][3], width=0)
                self.update()

                r,c = self.fromTo.pop(0)
                self.itemconfigure(self.squares[(r, c)][0], fill=self.squares[(r, c)][3], outline=self.squares[(r, c)][3], width=0)
                self.update()
    
    def en_passant(self):
        # making sure en_passant is removed after 1 turn passes
        for key, val in self.squares.items():
            if val[1] != None:
                if val[1].notation == "P" or val[1].notation == "Pb":
                    if val[1].do_en_pass == True and val[1].en_pass_count == 1:
                        # print(f"{val[1].color} pawn at ({val[1].pos_r},{val[1].pos_c}) do_en_pass was {val[1].do_en_pass} before")
                        val[1].do_en_pass = False
                        val[1].en_pass_count = 0
                        # print(f"{val[1].color} pawn at ({val[1].pos_r},{val[1].pos_c}) do_en_pass is now {val[1].do_en_pass}")
                    elif val[1].get_en_pass == True and val[1].en_pass_count == 1:
                        # print(f"{val[1].color} pawn at ({val[1].pos_r},{val[1].pos_c}) get_en_pass was {val[1].get_en_pass} before")
                        val[1].get_en_pass = False
                        val[1].en_pass_count = 0
                        # print(f"{val[1].color} pawn at ({val[1].pos_r},{val[1].pos_c}) get_en_pass is now {val[1].get_en_pass}")    

    def pinsChecksCheckmate(self):
        # Confirming pinned pieces and adjusting their legal moves based on the pin
        for key, val in self.squares.items():
            if val[1] != None:
                if val[1].notation != "K" and val[1].notation != "Kb":
                    if val[1].pinned == True:
                        pinners = []
                        for pinKey, pinVal in self.squares.items():
                            if pinVal[1] != None:
                                if pinVal[1].notation == "Q" or pinVal[1].notation == "Qb" or pinVal[1].notation == "B" or pinVal[1].notation == "Bb" or pinVal[1].notation == "R" or pinVal[1].notation == "Rb":
                                    if pinVal[1].pin_pathway:
                                        # print(f"Check pathway of {pinVal[1].notation}", pinVal[1].check_pathway)
                                        # print(f"Pin pathway of {pinVal[1].notation}", pinVal[1].pin_pathway)
                                        if (val[1].pos_r, val[1].pos_c) not in pinVal[1].pin_pathway:
                                            pinVal[1].pin_pathway.append((val[1].pos_r, val[1].pos_c))
                                            pinners.append(pinVal[1])
                                        else:
                                            pinners.append(pinVal[1])
                        # print("PINNERS:", pinners)
                        if len(pinners) > 1:
                            val[1].legal_moves = []
                        elif len(pinners) == 1:
                            legal_moves_of_pinned_piece = []
                            for legal in val[1].legal_moves:
                                if legal in pinners[0].pin_pathway or legal == (pinners[0].pos_r, pinners[0].pos_c):
                                    legal_moves_of_pinned_piece.append(legal)
                            val[1].legal_moves = legal_moves_of_pinned_piece
                            # print(f"I the {val[1].color} {val[1].notation} legal moves for me=", val[1].legal_moves)
                        # if len(self.clicked_piece.legal_moves) >= 1:
                        #     highlight = self.whiteHighlight if self.squares[(clicked_row, clicked_col)][3] == "#eaebc8" else self.greenHighlight
                        #     self.turns += 1
                        #     self.itemconfigure(square_id, fill=highlight, outline=highlight, width=0)
                        #     self.update()
                        #     self.clicked = square_id

                            # taking into account the turns that have occurred for any pawns granted en passant
                            # for key, val in self.squares.items():
                            #     if val[1] != None and (val[1].notation == "P" or val[1].notation == "Pb"):
                            #         if val[1].do_en_pass or val[1].get_en_pass:
                            #             val[1].en_pass_count += 1 # changing the en_pass_count from 0 to 1 so that it can be set to False in the move_piece function

                        #     self.bind("<Button-1>", lambda e: self.move_piece(e, r, c, square_id, self.clicked_piece))
                        # elif len(self.clicked_piece.legal_moves) >= 1:
                        #     highlight = self.whiteHighlight if self.squares[(clicked_row, clicked_col)][3] == "#eaebc8" else self.greenHighlight
                        #     self.turns += 1
                        #     self.itemconfigure(square_id, fill=highlight, outline=highlight, width=0)
                        #     self.update()
                        #     self.clicked = square_id

                        #     # taking into account the turns that have occurred for any pawns granted en passant
                        #     for key, val in self.squares.items():
                        #         if val[1] != None and (val[1].notation == "P" or val[1].notation == "Pb"):
                        #             if val[1].do_en_pass == True or val[1].get_en_pass:
                        #                 val[1].en_pass_count += 1 # changing the en_pass_count from 0 to 1 so that it can be set to False in the move_piece function

                        #     self.bind("<Button-1>", lambda e: self.move_piece(e, r, c, square_id, self.clicked_piece))

        black_check_pos = None
        white_check_pos = None

        # Updating the moves specifically for the King
        for key, val in self.squares.items():
            if val[1] != None:
                if val[1].notation == "K" or val[1].notation == "Kb":
                    val[1].legal_moves = self.get_legal_moves(val[1], val[1].pos_r, val[1].pos_c)

        # find current position of black and white king who may be in check
        for key, val in self.squares.items():
            if val[1] != None:
                if val[1].notation == "K":
                    if val[1].in_check:
                        white_check_pos = (val[1].pos_r,val[1].pos_c)
                        print('WHITE IS IN CHECK')
                elif val[1].notation == "Kb":
                    if val[1].in_check:
                        black_check_pos = (val[1].pos_r,val[1].pos_c)
                        print('BLACK IS IN CHECK')
        
        # if black_check_pos == None and white_check_pos == None:
        #     self.incheck_move = defaultdict(list)
        #     self.incheck_take = defaultdict(list)
        #     self.incheck_interpose = defaultdict(list)
        #     self.checkers = [] # This is needed because having one or multiple pieces checking the King can impact whether all or one of moving, taking, or interposing is possible
        #     self.check_on_the_board = False

        # handling the black king being in check
        if black_check_pos != None:
            self.check_on_the_board = True # this is now True so an action must be taken to get out of check

            for key, val in self.squares.items():
                    if val[1] != None:
                        # finding out which piece(s) has/have the king under attack 
                        if val[1].color == "white":
                            if black_check_pos in val[1].legal_moves:
                                self.checkers.append(val[1])
            
            # if there are multiple checkers then the only option is to move
            if len(self.checkers) > 1:
                if self.squares[black_check_pos][1].legal_moves:
                    self.incheck_move[black_check_pos] = self.squares[black_check_pos][1].legal_moves # King can ONLY move out of the way
            elif len(self.checkers) == 1:
                piece = self.checkers[0]
                
                if self.squares[black_check_pos][1].legal_moves:
                    self.incheck_move[black_check_pos] = self.squares[black_check_pos][1].legal_moves # King can simply move out of the way

                for key, val in self.squares.items():
                    if val[1] != None:
                        if (piece.pos_r, piece.pos_c) in val[1].legal_moves: # an ally piece takes the piece that's checked the king
                            self.incheck_take[(val[1].pos_r, val[1].pos_c)].append((piece.pos_r, piece.pos_c))
                
                interpose = []
                if piece.notation == "Q" or piece.notation == "B" or piece.notation == "R": # interposition
                    for key, val in self.squares.items():
                        if val[1] != None and val[1].color == "black":
                            for r,c in val[1].legal_moves:
                                if (r, c) in piece.check_pathway:
                                    interpose.append((r, c))
                            if interpose:
                                self.incheck_interpose[(val[1].pos_r, val[1].pos_c)] = interpose
                            interpose = []
                
                # print("I the black king am in check but I can move:", self.incheck_move)
                # print("I the black king am in check but someone can take:", self.incheck_take)
                # print("I the black king am in check but someone can interpose:", self.incheck_interpose)
        
        # handling the white king being in check
        if white_check_pos != None:
            self.check_on_the_board = True # this is now True so an action must be taken to get out of check

            for key, val in self.squares.items():
                    if val[1] != None:
                        # finding out which piece(s) has/have the king under attack 
                        if val[1].color == "black":
                            if white_check_pos in val[1].legal_moves:
                                self.checkers.append(val[1])
            
            # if there are multiple checkers then the only option is to move
            if len(self.checkers) > 1:
                if self.squares[white_check_pos][1].legal_moves:
                    self.incheck_move[white_check_pos] = self.squares[white_check_pos][1].legal_moves # King can ONLY move out of the way
            elif len(self.checkers) == 1:
                piece = self.checkers[0]
                
                if self.squares[white_check_pos][1].legal_moves:
                    self.incheck_move[white_check_pos] = self.squares[white_check_pos][1].legal_moves # King can simply move out of the way

                for key, val in self.squares.items():
                    if val[1] != None:
                        if (piece.pos_r, piece.pos_c) in val[1].legal_moves: # an ally piece takes the piece that's checked the king
                            self.incheck_take[(val[1].pos_r, val[1].pos_c)].append((piece.pos_r, piece.pos_c))
                
                interpose = []
                if piece.notation == "Qb" or piece.notation == "Bb" or piece.notation == "Rb": # interposition
                    for key, val in self.squares.items():
                        if val[1] != None and val[1].color == "white":
                            for r,c in val[1].legal_moves:
                                if (r, c) in piece.check_pathway:
                                    interpose.append((r, c))
                            if interpose:
                                self.incheck_interpose[(val[1].pos_r, val[1].pos_c)] = interpose
                            interpose = []
                
                # print("I the white king am in check but I can move:", self.incheck_move)
                # print("I the white king am in check but someone can take:", self.incheck_take)
                # print("I the white king am in check but someone can interpose:", self.incheck_interpose)
        
        # if black_check_pos:
        #     print(self.check_on_the_board)
        #     print(self.incheck_move)
        #     print(self.incheck_take)
        #     print(self.incheck_interpose)
        # if checkmate is found the game is over
        if self.check_on_the_board:
            if self.incheck_move == {} and self.incheck_take == {} and self.incheck_interpose == {}:
                messagebox.showinfo("Checkmate", "CHECKMATE White has won!") if self.turn_based[(self.turns) % 2] == "black" else messagebox.showinfo("Checkmate", "CHECKMATE Black has won!")
                self.turn_based = [None, None] # ensures the pieces can't be moved again

    def draws(self): # STILL IN DEVELOPMENT    
        # stalemate
        self.all_white_legal_moves = 0
        self.all_black_legal_moves = 0
        for key, val in self.squares.items():
            if val[1] != None:
                if val[1].color == "white":
                    self.all_white_legal_moves += len(val[1].legal_moves)
                else:
                    self.all_black_legal_moves += len(val[1].legal_moves)
        if self.all_white_legal_moves == 0 and self.turn_based[(self.turns) % 2] == "white":
            messagebox.showinfo("Draw", "STALEMATE there is no winner.")
            self.turn_based = [None, None] # ensures the pieces can't be moved again
        elif self.all_black_legal_moves == 0 and self.turn_based[(self.turns) % 2] == "black":
            messagebox.showinfo("Draw", "STALEMATE there is no winner.")
            self.turn_based = [None, None] # ensures the pieces can't be moved again  
        
        # insufficient material
        self.all_white_pieces = []
        self.all_black_pieces = []
        for key, val in self.squares.items():
            if val[1] != None:
                if val[1].color == "white":
                    self.all_white_pieces.append(val[1].notation)
                else:
                    self.all_black_pieces.append(val[1].notation)
        white_insufficient = False
        black_insufficient = False
        self.all_white_pieces = sorted(self.all_white_pieces)
        self.all_black_pieces = sorted(self.all_black_pieces)
        if self.all_white_pieces == ["K"] or self.all_white_pieces == ["K", "N"] or self.all_white_pieces == ["B", "K"]:
            white_insufficient = True
        if self.all_black_pieces == ["Kb"] or self.all_black_pieces == ["Kb", "Nb"] or self.all_black_pieces == ["Bb", "Kb"]:
            black_insufficient = True
        # print("white pieces left=", self.all_white_pieces)
        # print("black pieces left=", self.all_black_pieces)
        if white_insufficient and black_insufficient:
            messagebox.showinfo("Draw", "INSUFFICIENT MATING MATERIAL there is no winner.")
            self.turn_based = [None, None] # ensures the pieces can't be moved again

        # 3-fold repetition
        def are_board_states_equal(pos1, pos2):
            for r in range(0, 8):
                for c in range(0, 8):
                    if pos1[(r, c)][1] == None and pos2[(r, c)][1] == None:
                        continue
                    elif pos1[(r, c)][1] != None and pos2[(r, c)][1] != None:
                        if pos1[(r, c)][1].notation != pos2[(r, c)][1].notation:
                            # print(pos1[(r, c)][1].notation)
                            # print(pos2[(r, c)][1].notation)
                            # print("returning false")
                            return False
                    else:
                        # if pos1[(r, c)][1] != None:
                        #     # print(pos1[(r, c)][1].notation)
                        # if pos2[(r, c)][1] != None:
                        #     # print(pos2[(r, c)][1].notation)
                        # print("returning false")
                        return False
            return True
        self.game_states.append(copy.deepcopy(self.squares))
        repeated = False
        # print(len(self.game_states))
        for a in range(0, len(self.game_states)):
            for b in range(a + 1, len(self.game_states)):
                for c in range(b + 1, len(self.game_states)):
                    # print("ENTERED")
                    if are_board_states_equal(self.game_states[a], self.game_states[b]):
                        if are_board_states_equal(self.game_states[b], self.game_states[c]):
                            repeated = True
        if repeated:
            messagebox.showinfo("Draw", "3-FOLD REPETITION there is no winner.")
            self.turn_based = [None, None] # ensures the pieces can't be moved again
        
        # fifty move rule
        # print("FIFTY MOVE RULE=", self.fifty_move_rule)
        if self.fifty_move_rule == 50:
            messagebox.showinfo("Draw", "FIFTY MOVE RULE there is no winner.")
            self.turn_based = [None, None] # ensures the pieces can't be moved again

    def get_legal_moves(self, actual_piece, r, c, **kwargs):
        #region black KING get legal moves
        if actual_piece.notation == "Kb":
            add_legal_moves = []
            add_defends = []
            add_border = []

            # CASTLE queen side
            if (actual_piece.moved == False):
                if ((self.squares[(0,0)][1] != None)):
                    if ((self.squares[(0,0)][1].notation == "Rb")):
                        if ((self.squares[(0,0)][1].moved == False)):
                            if (self.squares[(0,1)][1] == None) and (self.squares[(0,2)][1] == None) and (self.squares[(0,3)][1] == None):
                                # By this point the King and queen side Rook haven't moved and have nothing in between them.
                                # But what also must be checked is whether or not an enemy piece has a legal_move of one of the squares that are inbetween the King and Rook
                                add_legal_moves.append((0,2))
                                for key, val in self.squares.items():
                                    if val[1] != None:
                                        if val[1].color == "white":
                                            if (0, 1) in val[1].legal_moves or (0, 2) in val[1].legal_moves or (0, 3) in val[1].legal_moves:
                                                add_legal_moves.remove((0,2))
            else:
                if (0,2) in actual_piece.legal_moves:
                    actual_piece.legal_moves.remove((0,2))

            # CASTLE king side
            if (actual_piece.moved == False):
                if ((self.squares[(0,7)][1] != None)):
                    if ((self.squares[(0,7)][1].notation == "Rb")):
                        if ((self.squares[(0,7)][1].moved == False)):
                            if (self.squares[(0,5)][1] == None) and (self.squares[(0,6)][1] == None):
                                add_legal_moves.append((0,6))
                                for key, val in self.squares.items():
                                    if val[1] != None:
                                        if val[1].color == "white":
                                            if (0, 5) in val[1].legal_moves or (0, 6) in val[1].legal_moves:
                                                add_legal_moves.remove((0,6))
            else:
                if (0,6) in actual_piece.legal_moves:
                    actual_piece.legal_moves.remove((0,6))
            
            for i in range(1,2):
                if r-i < 0 or c-i < 0:
                    i=2
                    break
                elif (self.squares[(r-i,c-i)][1] != None):
                    add_border.append((r-i,c-i)) 

                    # enemy piece to the diagonal top left
                    if (self.squares[(r-i,c-i)][1].color != actual_piece.color):
                        add_legal_moves.append((r-i,c-i))
                        # make sure king can't move to legal or defended spaces of enemy pieces
                        for key, val in self.squares.items():
                            if val[1] != None and ((r-i,c-i) in add_legal_moves):
                                
                                # I make sure to break after removing the square from the king's legal moves so that no other pieces are checked
                                if val[1].notation == "B":
                                    if((r-i,c-i) in val[1].legal_moves) or ((r-i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c-i))
                                        break
                                if val[1].notation == "R":
                                    if((r-i,c-i) in val[1].legal_moves) or ((r-i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c-i))
                                        break
                                if val[1].notation == "P":
                                    # checking the diagonals of the white Pawn
                                    if((r-i,c-i) == (val[1].pos_r-1,val[1].pos_c-1)) or ((r-i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c-i))
                                        break
                                    if ((r-i,c-i) == (val[1].pos_r-1,val[1].pos_c+1)) or ((r-i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c-i))
                                        break
                                if val[1].notation == "Q":
                                    if((r-i,c-i) in val[1].legal_moves) or ((r-i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c-i))
                                        break
                                if val[1].notation == "N":
                                    if((r-i,c-i) in val[1].legal_moves) or ((r-i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c-i))
                                        break
                                if val[1].notation == "K":  
                                    if((r-i,c-i) in val[1].legal_moves) or ((r-i,c-i) in val[1].defends) or ((r-i,c-i) in val[1].border):
                                        add_legal_moves.remove((r-i,c-i))
                                        break
                    # ally piece to the diagonal top left
                    else:
                        add_border.append((r-i,c-i))

                        add_defends.append((r-i,c-i))
                        i=2
                        break
                # no piece to the diagonal top left
                elif (self.squares[(r-i,c-i)][1] == None):
                    add_border.append((r-i,c-i))

                    add_legal_moves.append((r-i,c-i))
                    # make sure king can't move to legal or attack spaces of opposing pieces
                    for key, val in self.squares.items():
                        if val[1] != None and ((r-i,c-i) in add_legal_moves):
                            if val[1].notation == "B":
                                if((r-i,c-i) in val[1].legal_moves) or ((r-i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c-i))
                                    break
                            if val[1].notation == "R":
                                if((r-i,c-i) in val[1].legal_moves) or ((r-i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c-i))
                                    break
                            if val[1].notation == "P":
                                # checking the diagonals of the white Pawn
                                if((r-i,c-i) == (val[1].pos_r-1,val[1].pos_c-1)) or ((r-i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c-i))
                                    break
                                if ((r-i,c-i) == (val[1].pos_r-1,val[1].pos_c+1)) or ((r-i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c-i))
                                    break
                            if val[1].notation == "Q":
                                if((r-i,c-i) in val[1].legal_moves) or ((r-i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c-i))
                                    break
                            if val[1].notation == "N":
                                if((r-i,c-i) in val[1].legal_moves) or ((r-i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c-i))
                                    break
                            if val[1].notation == "K":  
                                if((r-i,c-i) in val[1].legal_moves) or ((r-i,c-i) in val[1].defends) or ((r-i,c-i) in val[1].border):
                                    add_legal_moves.remove((r-i,c-i))
                                    break
            
            for i in range(1,2):
                if r+i > 7 or c-i < 0:
                    i=2
                    break
                elif (self.squares[(r+i,c-i)][1] != None): 
                    add_border.append((r+i,c-i))

                    # enemy piece to the diagonal bottom left
                    if (self.squares[(r+i,c-i)][1].color != actual_piece.color):
                        add_legal_moves.append((r+i,c-i))
                        # make sure king can't move to legal or attack spaces of opposing pieces
                        for key, val in self.squares.items():
                            if val[1] != None and ((r+i,c-i) in add_legal_moves):
                                if val[1].notation == "B":
                                    if((r+i,c-i) in val[1].legal_moves) or ((r+i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c-i))
                                        break
                                if val[1].notation == "R":
                                    if((r+i,c-i) in val[1].legal_moves) or ((r+i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c-i))
                                        break
                                if val[1].notation == "P":
                                    # checking the diagonals of the white Pawn
                                    if((r+i,c-i) == (val[1].pos_r-1,val[1].pos_c-1)) or ((r+i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c-i))
                                        break
                                    if ((r+i,c-i) == (val[1].pos_r-1,val[1].pos_c+1)) or ((r+i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c-i))
                                        break
                                if val[1].notation == "Q":
                                    if((r+i,c-i) in val[1].legal_moves) or ((r+i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c-i))
                                        break
                                if val[1].notation == "N":
                                    if((r+i,c-i) in val[1].legal_moves) or ((r+i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c-i))
                                        break
                                if val[1].notation == "K":  
                                    if((r+i,c-i) in val[1].legal_moves) or ((r+i,c-i) in val[1].defends) or ((r+i,c-i) in val[1].border):
                                        add_legal_moves.remove((r+i,c-i))
                                        break
                    # ally piece to the diagonal bottom left
                    else:
                        add_border.append((r+i,c-i))

                        add_defends.append((r+i,c-i))
                        i=2
                        break
                # no piece to the diagonal bottom left
                elif (self.squares[(r+i,c-i)][1] == None): 
                    add_border.append((r+i,c-i))

                    add_legal_moves.append((r+i,c-i))
                    # make sure king can't move to legal or attack spaces of opposing pieces
                    for key, val in self.squares.items():
                        if val[1] != None and ((r+i,c-i) in add_legal_moves):
                            if val[1].notation == "B":
                                if((r+i,c-i) in val[1].legal_moves) or ((r+i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c-i))
                                    break
                            if val[1].notation == "R":
                                if((r+i,c-i) in val[1].legal_moves) or ((r+i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c-i))
                                    break
                            if val[1].notation == "P":
                                # checking the diagonals of the white Pawn
                                if((r+i,c-i) == (val[1].pos_r-1,val[1].pos_c-1)) or ((r+i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c-i))
                                    break
                                if ((r+i,c-i) == (val[1].pos_r-1,val[1].pos_c+1)) or ((r+i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c-i))
                                    break
                            if val[1].notation == "Q":
                                if((r+i,c-i) in val[1].legal_moves) or ((r+i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c-i))
                                    break
                            if val[1].notation == "N":
                                if((r+i,c-i) in val[1].legal_moves) or ((r+i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c-i))
                                    break
                            if val[1].notation == "K":  
                                if((r+i,c-i) in val[1].legal_moves) or ((r+i,c-i) in val[1].defends) or ((r+i,c-i) in val[1].border):
                                    add_legal_moves.remove((r+i,c-i))
                                    break

            for i in range(1,2):
                if r-i < 0 or c+i > 7:
                    i=2
                    break
                elif (self.squares[(r-i,c+i)][1] != None): 
                    add_border.append((r-i,c+i))

                    # enemy piece to the diagonal top right
                    if (self.squares[(r-i,c+i)][1].color != actual_piece.color):
                        add_legal_moves.append((r-i,c+i))
                        # make sure king can't move to legal or attack spaces of opposing pieces
                        for key, val in self.squares.items():
                            if val[1] != None and ((r-i,c+i) in add_legal_moves):
                                if val[1].notation == "B":
                                    if((r-i,c+i) in val[1].legal_moves) or ((r-i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c+i))
                                        break
                                if val[1].notation == "R":
                                    if((r-i,c+i) in val[1].legal_moves) or ((r-i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c+i))
                                        break
                                if val[1].notation == "P":
                                    # checking the diagonals of the white Pawn
                                    if((r-i,c+i) == (val[1].pos_r-1,val[1].pos_c-1)) or ((r-i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c+i))
                                        break
                                    if ((r-i,c+i) == (val[1].pos_r-1,val[1].pos_c+1)) or ((r-i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c+i))
                                        break
                                if val[1].notation == "Q":
                                    if((r-i,c+i) in val[1].legal_moves) or ((r-i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c+i))
                                        break
                                if val[1].notation == "N":
                                    if((r-i,c+i) in val[1].legal_moves) or ((r-i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c+i))
                                        break
                                if val[1].notation == "K":  
                                    if((r-i,c+i) in val[1].legal_moves) or ((r-i,c+i) in val[1].defends) or ((r-i,c+i) in val[1].border):
                                        add_legal_moves.remove((r-i,c+i))
                                        break
                    # ally piece to the diagonal top right
                    else:
                        add_border.append((r-i,c+i))

                        add_defends.append((r-i,c+i))
                        i=2
                        break
                # no piece to the diagonal top right
                elif (self.squares[(r-i,c+i)][1] == None): 
                    add_border.append((r-i,c+i))

                    add_legal_moves.append((r-i,c+i))
                    # make sure king can't move to legal or attack spaces of opposing pieces
                    for key, val in self.squares.items():
                        if val[1] != None and ((r-i,c+i) in add_legal_moves):
                            if val[1].notation == "B":
                                if((r-i,c+i) in val[1].legal_moves) or ((r-i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c+i))
                                    break
                            if val[1].notation == "R":
                                if((r-i,c+i) in val[1].legal_moves) or ((r-i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c+i))
                                    break
                            if val[1].notation == "P":
                                # checking the diagonals of the white Pawn
                                if((r-i,c+i) == (val[1].pos_r-1,val[1].pos_c-1)) or ((r-i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c+i))
                                    break
                                if ((r-i,c+i) == (val[1].pos_r-1,val[1].pos_c+1)) or ((r-i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c+i))
                                    break
                            if val[1].notation == "Q":
                                if((r-i,c+i) in val[1].legal_moves) or ((r-i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c+i))
                                    break
                            if val[1].notation == "N":
                                if((r-i,c+i) in val[1].legal_moves) or ((r-i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c+i))
                                    break
                            if val[1].notation == "K":  
                                if((r-i,c+i) in val[1].legal_moves) or ((r-i,c+i) in val[1].defends) or ((r-i,c+i) in val[1].border):
                                    add_legal_moves.remove((r-i,c+i))
                                    break

            for i in range(1,2):
                if r+i > 7 or c+i > 7: 
                    i=2
                    break
                elif (self.squares[(r+i,c+i)][1] != None): 
                    add_border.append((r+i,c+i))

                    # enemy piece to the diagonal bottom right
                    if (self.squares[(r+i,c+i)][1].color != actual_piece.color):
                        add_legal_moves.append((r+i,c+i))
                        # make sure king can't move to legal or attack spaces of opposing pieces
                        for key, val in self.squares.items():
                            if val[1] != None and ((r+i,c+i) in add_legal_moves):
                                if val[1].notation == "B":
                                    if((r+i,c+i) in val[1].legal_moves) or ((r+i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c+i))
                                        break
                                if val[1].notation == "R":
                                    if((r+i,c+i) in val[1].legal_moves) or ((r+i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c+i))
                                        break
                                if val[1].notation == "P":
                                    # checking the diagonals of the white Pawn
                                    if((r+i,c+i) == (val[1].pos_r-1,val[1].pos_c-1)) or ((r+i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c+i))
                                        break
                                    if ((r+i,c+i) == (val[1].pos_r-1,val[1].pos_c+1)) or ((r+i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c+i))
                                        break
                                if val[1].notation == "Q":
                                    if((r+i,c+i) in val[1].legal_moves) or ((r+i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c+i))
                                        break
                                if val[1].notation == "N":
                                    if((r+i,c+i) in val[1].legal_moves) or ((r+i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c+i))
                                        break
                                if val[1].notation == "K":  
                                    if((r+i,c+i) in val[1].legal_moves) or ((r+i,c+i) in val[1].defends) or ((r+i,c+i) in val[1].border):
                                        add_legal_moves.remove((r+i,c+i))
                                        break
                    # ally piece to the diagonal bottom right
                    else:
                        add_border.append((r+i,c+i))

                        add_defends.append((r+i,c+i))
                        i=2
                        break
                # no piece to the diagonal bottom right
                elif (self.squares[(r+i,c+i)][1] == None): 
                    add_border.append((r+i,c+i))

                    add_legal_moves.append((r+i,c+i))
                    # make sure king can't move to legal or attack spaces of opposing pieces
                    for key, val in self.squares.items():
                        if val[1] != None and ((r+i,c+i) in add_legal_moves):
                            if val[1].notation == "B":
                                if((r+i,c+i) in val[1].legal_moves) or ((r+i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c+i))
                                    break
                            if val[1].notation == "R":
                                if((r+i,c+i) in val[1].legal_moves):
                                    add_legal_moves.remove((r+i,c+i))
                                    break
                            if val[1].notation == "P":
                                # checking the diagonals of the white Pawn
                                if((r+i,c+i) == (val[1].pos_r-1,val[1].pos_c-1)) or ((r+i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c+i))
                                    break
                                if ((r+i,c+i) == (val[1].pos_r-1,val[1].pos_c+1)) or ((r+i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c+i))
                                    break
                            if val[1].notation == "Q":
                                if((r+i,c+i) in val[1].legal_moves) or ((r+i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c+i))
                                    break
                            if val[1].notation == "N":
                                if((r+i,c+i) in val[1].legal_moves) or ((r+i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c+i))
                                    break
                            if val[1].notation == "K":  
                                if((r+i,c+i) in val[1].legal_moves) or ((r+i,c+i) in val[1].defends) or ((r+i,c+i) in val[1].border):
                                    add_legal_moves.remove((r+i,c+i))
                                    break
            
            for i in range(c,c-2,-1):
                if i == c:
                    continue
                elif i < 0 or i > 7: 
                    i=c-2
                    break
                elif (self.squares[(r,i)][1] != None): 
                    add_border.append((r,i))

                    # enemy piece to the left
                    if (self.squares[(r,i)][1].color != actual_piece.color):
                        add_legal_moves.append((r,i))
                        # make sure king can't move to legal or attack spaces of opposing pieces
                        for key, val in self.squares.items():
                            if val[1] != None and ((r,i) in add_legal_moves):
                                if val[1].notation == "B":
                                    if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                if val[1].notation == "R":
                                    if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                if val[1].notation == "P":
                                    # checking the diagonals of the white Pawn
                                    if((r,i) == (val[1].pos_r-1,val[1].pos_c-1)) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                    if ((r,i) == (val[1].pos_r-1,val[1].pos_c+1)) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                if val[1].notation == "Q":
                                    if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                if val[1].notation == "N":
                                    if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                if val[1].notation == "K":  
                                    if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends) or ((r,i) in val[1].border):
                                        add_legal_moves.remove((r,i))
                                        break
                    # ally piece to the left
                    else:
                        add_border.append((r,i))

                        add_defends.append((r,i))
                        i=c-2
                        break
                # no piece to the left
                elif (self.squares[(r,i)][1] == None): 
                    add_border.append((r,i))

                    add_legal_moves.append((r,i))
                    # make sure king can't move to legal or attack spaces of opposing pieces
                    for key, val in self.squares.items():
                        if val[1] != None and ((r,i) in add_legal_moves):
                            if val[1].notation == "B":
                                if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                            if val[1].notation == "R":
                                if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                            if val[1].notation == "P":
                                # checking the diagonals of the white Pawn
                                if((r,i) == (val[1].pos_r-1,val[1].pos_c-1)) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                                if ((r,i) == (val[1].pos_r-1,val[1].pos_c+1)) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                            if val[1].notation == "Q":
                                if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                            if val[1].notation == "N":
                                if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                            if val[1].notation == "K":  
                                if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends) or ((r,i) in val[1].border):
                                    add_legal_moves.remove((r,i))
                                    break

            for i in range(c,c+2):
                if i == c:
                    continue
                elif i < 0 or i > 7: 
                    i=c+2
                    break
                elif (self.squares[(r,i)][1] != None): 
                    add_border.append((r,i))

                    # enemy piece to the right
                    if (self.squares[(r,i)][1].color != actual_piece.color):
                        add_legal_moves.append((r,i))
                        # make sure king can't move to legal or attack spaces of opposing pieces
                        for key, val in self.squares.items():
                            if val[1] != None and ((r,i) in add_legal_moves):                         
                                if val[1].notation == "B":
                                    if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                elif val[1].notation == "R":
                                    if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                elif val[1].notation == "P":
                                    # checking the diagonals of the white Pawn
                                    if((r,i) == (val[1].pos_r-1,val[1].pos_c-1)) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                    if ((r,i) == (val[1].pos_r-1,val[1].pos_c+1)) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                elif val[1].notation == "Q":
                                    if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                elif val[1].notation == "N":
                                    if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                elif val[1].notation == "K":  
                                    if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends) or ((r,i) in val[1].border):
                                        add_legal_moves.remove((r,i))
                                        break
                    # ally piece to the right
                    else:
                        add_border.append((r,i))

                        add_defends.append((r,i))
                        i=c+2
                        break
                # no piece to the right
                elif (self.squares[(r,i)][1] == None): 
                    add_border.append((r,i))

                    add_legal_moves.append((r,i))
                    # make sure king can't move to legal or attack spaces of opposing pieces
                    for key, val in self.squares.items():
                        if val[1] != None and ((r,i) in add_legal_moves):
                            if val[1].notation == "B":
                                if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                            if val[1].notation == "R":
                                if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                            if val[1].notation == "P":
                                # checking the diagonals of the white Pawn
                                if((r,i) == (val[1].pos_r-1,val[1].pos_c-1)) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                                if((r,i) == (val[1].pos_r-1,val[1].pos_c+1)) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i)) 
                                    break
                            if val[1].notation == "Q":
                                if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                            if val[1].notation == "N":
                                if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                            if val[1].notation == "K":  
                                if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends) or ((r,i) in val[1].border):
                                    add_legal_moves.remove((r,i))
                                    break

            for i in range(r,r-2,-1):
                if i == r:
                    continue
                elif i < 0 or i > 7: 
                    i=r-2
                    break
                elif (self.squares[(i,c)][1] != None):
                    add_border.append((i,c))

                    # enemy piece above
                    if (self.squares[(i,c)][1].color != actual_piece.color):
                        add_legal_moves.append((i,c))
                        # make sure king can't move to legal or attack spaces of opposing pieces
                        for key, val in self.squares.items():
                            if val[1] != None and ((i,c) in add_legal_moves):
                                if val[1].notation == "B":
                                    if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                if val[1].notation == "R":
                                    if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                if val[1].notation == "P":
                                    # checking the diagonals of the white Pawn
                                    if((i,c) == (val[1].pos_r-1,val[1].pos_c-1)) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                    if ((i,c) == (val[1].pos_r-1,val[1].pos_c+1)) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                if val[1].notation == "Q":
                                    if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                if val[1].notation == "N":
                                    if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                if val[1].notation == "K":  
                                    if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends) or ((i,c) in val[1].border):
                                        add_legal_moves.remove((i,c))
                                        break
                    # ally piece above
                    else:
                        add_border.append((i,c))

                        add_defends.append((i,c))
                        i=r-2
                        break
                # no piece above
                elif (self.squares[(i,c)][1] == None):
                    add_border.append((i,c))

                    add_legal_moves.append((i,c))
                    # make sure king can't move to legal or attack spaces of opposing pieces
                    for key, val in self.squares.items():
                        if val[1] != None and ((i,c) in add_legal_moves):
                            if val[1].notation == "B": 
                                if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                            if val[1].notation == "R":
                                if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                            if val[1].notation == "P":
                                # checking the diagonals of the white Pawn
                                if((i,c) == (val[1].pos_r-1,val[1].pos_c-1)) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                                if ((i,c) == (val[1].pos_r-1,val[1].pos_c+1)) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                            if val[1].notation == "Q":
                                if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                            if val[1].notation == "N":
                                if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                            if val[1].notation == "K":  
                                if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends) or ((i,c) in val[1].border):
                                    add_legal_moves.remove((i,c))
                                    break

            for i in range(r,r+2):
                if i == r:
                    continue
                elif i < 0 or i > 7: 
                    i=r+2
                    break
                elif (self.squares[(i,c)][1] != None): 
                    add_border.append((i,c))

                    # enemy piece below
                    if (self.squares[(i,c)][1].color != actual_piece.color):
                        add_legal_moves.append((i,c))
                        # make sure king can't move to legal or attack spaces of opposing pieces
                        for key, val in self.squares.items():
                            if val[1] != None and ((i,c) in add_legal_moves):
                                if val[1].notation == "B":
                                    if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                if val[1].notation == "R":
                                    if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                if val[1].notation == "P":
                                    # checking the diagonals of the white Pawn
                                    if((i,c) == (val[1].pos_r-1,val[1].pos_c-1)) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                    if ((i,c) == (val[1].pos_r-1,val[1].pos_c+1)) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                if val[1].notation == "Q":
                                    if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                if val[1].notation == "N":
                                    if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                if val[1].notation == "K":  
                                    if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends) or ((i,c) in val[1].border):
                                        add_legal_moves.remove((i,c))
                                        break
                    # ally piece below
                    else:
                        add_border.append((i,c))

                        add_defends.append((i,c))
                        i=r+2
                        break
                # no piece below
                elif (self.squares[(i,c)][1] == None):
                    add_border.append((i,c))

                    add_legal_moves.append((i,c))
                    # make sure king can't move to legal or attack spaces of opposing pieces
                    for key, val in self.squares.items():
                        if val[1] != None and ((i,c) in add_legal_moves):
                            if val[1].notation == "B":
                                if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                            if val[1].notation == "R":
                                if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                            if val[1].notation == "P":
                                # checking the diagonals of the white Pawn
                                if((i,c) == (val[1].pos_r-1,val[1].pos_c-1)) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                                if ((i,c) == (val[1].pos_r-1,val[1].pos_c+1)) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                            if val[1].notation == "Q":
                                if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                            if val[1].notation == "N":
                                if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                            if val[1].notation == "K":  
                                if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends) or ((i,c) in val[1].border):
                                    add_legal_moves.remove((i,c))
                                    break
            
            new_add_border = []
            for border in add_border:
                if border not in new_add_border:
                    new_add_border.append(border)

            actual_piece.defends = add_defends
            actual_piece.border = new_add_border
            return add_legal_moves
        #endregion

        #region white KING get legal moves
        if actual_piece.notation == "K": 
            add_legal_moves = []
            add_defends = []
            add_border = []

            # CASTLE queen side
            if (actual_piece.moved == False):
                if ((self.squares[(7,0)][1] != None)):
                    if ((self.squares[(7,0)][1].notation == "R")):
                        if ((self.squares[(7,0)][1].moved == False)):
                            if (self.squares[(7,1)][1] == None) and (self.squares[(7,2)][1] == None) and (self.squares[(7,3)][1] == None):
                                add_legal_moves.append((7,2))
                                for key, val in self.squares.items():
                                    if val[1] != None:
                                        if val[1].color == "black":
                                            if (7,1) in val[1].legal_moves or (7,2) in val[1].legal_moves or (7,3) in val[1].legal_moves:
                                                add_legal_moves.remove((7,2))
            else:
                if (0,2) in actual_piece.legal_moves:
                    actual_piece.legal_moves.remove((0,2))

            # CASTLE king side
            if (actual_piece.moved == False):
                if ((self.squares[(7,7)][1] != None)):
                    if ((self.squares[(7,7)][1].notation == "R")):
                        if ((self.squares[(7,7)][1].moved == False)):
                            if (self.squares[(7,5)][1] == None) and (self.squares[(7,6)][1] == None):
                                add_legal_moves.append((7,6))
                                for key, val in self.squares.items():
                                    if val[1] != None:
                                        if val[1].color == "black":
                                            if (7,5) in val[1].legal_moves or (7,6) in val[1].legal_moves:
                                                add_legal_moves.remove((7,6))
            else:
                if (0,2) in actual_piece.legal_moves:
                    actual_piece.legal_moves.remove((0,2))
            
            for i in range(1,2):
                if r-i < 0 or c-i < 0:
                    i=2
                    break
                elif (self.squares[(r-i,c-i)][1] != None):
                    add_border.append((r-i,c-i))

                    # enemy piece to the diagonal top left
                    if (self.squares[(r-i,c-i)][1].color != actual_piece.color):
                        add_legal_moves.append((r-i,c-i))
                        # make sure king can't move to legal or defended spaces of enemy pieces
                        for key, val in self.squares.items():
                            if val[1] != None and ((r-i,c-i) in add_legal_moves):
                                
                                # I make sure to break after removing the square from the king's legal moves so that no other pieces are checked
                                if val[1].notation == "Bb":
                                    if((r-i,c-i) in val[1].legal_moves) or ((r-i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c-i))
                                        break
                                if val[1].notation == "Rb":
                                    if((r-i,c-i) in val[1].legal_moves) or ((r-i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c-i))
                                        break
                                if val[1].notation == "Pb":
                                    # checking the diagonals of the black Pawn
                                    if((r-i,c-i) == (val[1].pos_r+1,val[1].pos_c-1)) or ((r-i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c-i))
                                        break
                                    if ((r-i,c-i) == (val[1].pos_r+1,val[1].pos_c+1)) or ((r-i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c-i))
                                        break
                                if val[1].notation == "Qb":
                                    if((r-i,c-i) in val[1].legal_moves) or ((r-i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c-i))
                                        break
                                if val[1].notation == "Nb":
                                    if((r-i,c-i) in val[1].legal_moves) or ((r-i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c-i))
                                        break
                                if val[1].notation == "Kb":  
                                    if((r-i,c-i) in val[1].legal_moves) or ((r-i,c-i) in val[1].defends) or ((r-i,c-i) in val[1].border):
                                        add_legal_moves.remove((r-i,c-i))
                                        break
                    # ally piece to the diagonal top left
                    else:
                        # print("ALLY to the diagonal top left")

                        add_border.append((r-i,c-i))

                        add_defends.append((r-i,c-i))
                        i=2
                        break
                # no piece to the diagonal top left
                elif (self.squares[(r-i,c-i)][1] == None):
                    add_border.append((r-i,c-i))

                    add_legal_moves.append((r-i,c-i))
                    # make sure king can't move to legal or attack spaces of opposing pieces
                    for key, val in self.squares.items():
                        if val[1] != None and ((r-i,c-i) in add_legal_moves):
                            if val[1].notation == "Bb":
                                if((r-i,c-i) in val[1].legal_moves) or ((r-i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c-i))
                                    break
                            if val[1].notation == "Rb":
                                if((r-i,c-i) in val[1].legal_moves) or ((r-i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c-i))
                                    break
                            if val[1].notation == "Pb":
                                # checking the diagonals of the black Pawn
                                if((r-i,c-i) == (val[1].pos_r+1,val[1].pos_c-1)) or ((r-i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c-i))
                                    break
                                if ((r-i,c-i) == (val[1].pos_r+1,val[1].pos_c+1)) or ((r-i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c-i))
                                    break
                            if val[1].notation == "Qb":
                                if((r-i,c-i) in val[1].legal_moves) or ((r-i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c-i))
                                    break
                            if val[1].notation == "Nb":
                                if((r-i,c-i) in val[1].legal_moves) or ((r-i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c-i))
                                    break
                            if val[1].notation == "Kb":  
                                if((r-i,c-i) in val[1].legal_moves) or ((r-i,c-i) in val[1].defends) or ((r-i,c-i) in val[1].border):
                                    add_legal_moves.remove((r-i,c-i))
                                    break
                    
            
            for i in range(1,2):
                if r+i > 7 or c-i < 0:
                    i=2
                    break
                elif (self.squares[(r+i,c-i)][1] != None): 
                    add_border.append((r+i,c-i))

                    # enemy piece to the diagonal bottom left
                    if (self.squares[(r+i,c-i)][1].color != actual_piece.color):
                        add_legal_moves.append((r+i,c-i))
                        # make sure king can't move to legal or attack spaces of opposing pieces
                        for key, val in self.squares.items():
                            if val[1] != None and ((r+i,c-i) in add_legal_moves):
                                if val[1].notation == "Bb":
                                    if((r+i,c-i) in val[1].legal_moves) or ((r+i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c-i))
                                        break
                                if val[1].notation == "Rb":
                                    if((r+i,c-i) in val[1].legal_moves) or ((r+i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c-i))
                                        break
                                if val[1].notation == "Pb":
                                    # checking the diagonals of the black Pawn
                                    if((r+i,c-i) == (val[1].pos_r+1,val[1].pos_c-1)) or ((r+i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c-i))
                                        break
                                    if ((r+i,c-i) == (val[1].pos_r+1,val[1].pos_c+1)) or ((r+i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c-i))
                                        break
                                if val[1].notation == "Qb":
                                    if((r+i,c-i) in val[1].legal_moves) or ((r+i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c-i))
                                        break
                                if val[1].notation == "Nb":
                                    if((r+i,c-i) in val[1].legal_moves) or ((r+i,c-i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c-i))
                                        break
                                if val[1].notation == "Kb":  
                                    if((r+i,c-i) in val[1].legal_moves) or ((r+i,c-i) in val[1].defends) or ((r+i,c-i) in val[1].border):
                                        add_legal_moves.remove((r+i,c-i))
                                        break
                    # ally piece to the diagonal bottom left
                    else:
                        # print("ALLY to the diagonal bottom left")

                        add_border.append((r+i,c-i))

                        add_defends.append((r+i,c-i))
                        i=2
                        break
                # no piece to the diagonal bottom left
                elif (self.squares[(r+i,c-i)][1] == None): 
                    add_border.append((r+i,c-i))

                    add_legal_moves.append((r+i,c-i))
                    # make sure king can't move to legal or attack spaces of opposing pieces
                    for key, val in self.squares.items():
                        if val[1] != None and ((r+i,c-i) in add_legal_moves):
                            if val[1].notation == "Bb":
                                if((r+i,c-i) in val[1].legal_moves) or ((r+i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c-i))
                                    break
                            if val[1].notation == "Rb":
                                if((r+i,c-i) in val[1].legal_moves) or ((r+i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c-i))
                                    break
                            if val[1].notation == "Pb":
                                # checking the diagonals of the black Pawn
                                if((r+i,c-i) == (val[1].pos_r+1,val[1].pos_c-1)) or ((r+i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c-i))
                                    break
                                if ((r+i,c-i) == (val[1].pos_r+1,val[1].pos_c+1)) or ((r+i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c-i))
                                    break
                            if val[1].notation == "Qb":
                                if((r+i,c-i) in val[1].legal_moves) or ((r+i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c-i))
                                    break
                            if val[1].notation == "Nb":
                                if((r+i,c-i) in val[1].legal_moves) or ((r+i,c-i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c-i))
                                    break
                            if val[1].notation == "Kb":  
                                if((r+i,c-i) in val[1].legal_moves) or ((r+i,c-i) in val[1].defends) or ((r+i,c-i) in val[1].border):
                                    add_legal_moves.remove((r+i,c-i))
                                    break

            for i in range(1,2):
                if r-i < 0 or c+i > 7:
                    i=2
                    break
                elif (self.squares[(r-i,c+i)][1] != None): 
                    add_border.append((r-i,c+i))

                    # enemy piece to the diagonal top right
                    if (self.squares[(r-i,c+i)][1].color != actual_piece.color):
                        add_legal_moves.append((r-i,c+i))
                        # make sure king can't move to legal or attack spaces of opposing pieces
                        for key, val in self.squares.items():
                            if val[1] != None and ((r-i,c+i) in add_legal_moves):
                                if val[1].notation == "Bb":
                                    if((r-i,c+i) in val[1].legal_moves) or ((r-i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c+i))
                                        break
                                if val[1].notation == "Rb":
                                    if((r-i,c+i) in val[1].legal_moves) or ((r-i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c+i))
                                        break
                                if val[1].notation == "Pb":
                                    # checking the diagonals of the black Pawn
                                    if((r-i,c+i) == (val[1].pos_r+1,val[1].pos_c-1)) or ((r-i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c+i))
                                        break
                                    if ((r-i,c+i) == (val[1].pos_r+1,val[1].pos_c+1)) or ((r-i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c+i))
                                        break
                                if val[1].notation == "Qb":
                                    if((r-i,c+i) in val[1].legal_moves) or ((r-i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c+i))
                                        break
                                if val[1].notation == "Nb":
                                    if((r-i,c+i) in val[1].legal_moves) or ((r-i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r-i,c+i))
                                        break
                                if val[1].notation == "Kb":  
                                    if((r-i,c+i) in val[1].legal_moves) or ((r-i,c+i) in val[1].defends) or ((r-i,c+i) in val[1].border):
                                        add_legal_moves.remove((r-i,c+i))
                                        break
                    # ally piece to the diagonal top right
                    else:
                        # print("ALLY to the diagonal top right")

                        add_border.append((r-i,c+i))

                        add_defends.append((r-i,c+i))
                        i=2
                        break
                # no piece to the diagonal top right
                elif (self.squares[(r-i,c+i)][1] == None): 
                    add_border.append((r-i,c+i))

                    add_legal_moves.append((r-i,c+i))
                    # make sure king can't move to legal or attack spaces of opposing pieces
                    for key, val in self.squares.items():
                        if val[1] != None and ((r-i,c+i) in add_legal_moves):
                            if val[1].notation == "Bb":
                                if((r-i,c+i) in val[1].legal_moves) or ((r-i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c+i))
                                    break
                            if val[1].notation == "Rb":
                                if((r-i,c+i) in val[1].legal_moves) or ((r-i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c+i))
                                    break
                            if val[1].notation == "Pb":
                                # checking the diagonals of the black Pawn
                                if((r-i,c+i) == (val[1].pos_r+1,val[1].pos_c-1)) or ((r-i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c+i))
                                    break
                                if ((r-i,c+i) == (val[1].pos_r+1,val[1].pos_c+1)) or ((r-i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c+i))
                                    break
                            if val[1].notation == "Qb":
                                if((r-i,c+i) in val[1].legal_moves) or ((r-i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c+i))
                                    break
                            if val[1].notation == "Nb":
                                if((r-i,c+i) in val[1].legal_moves) or ((r-i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r-i,c+i))
                                    break
                            if val[1].notation == "Kb":  
                                if((r-i,c+i) in val[1].legal_moves) or ((r-i,c+i) in val[1].defends) or ((r-i,c+i) in val[1].border):
                                    add_legal_moves.remove((r-i,c+i))
                                    break

            for i in range(1,2):
                if r+i > 7 or c+i > 7: 
                    i=2
                    break
                elif (self.squares[(r+i,c+i)][1] != None): 
                    add_border.append((r+i,c+i))

                    # enemy piece to the diagonal bottom right
                    if (self.squares[(r+i,c+i)][1].color != actual_piece.color):
                        add_legal_moves.append((r+i,c+i))
                        # make sure king can't move to legal or attack spaces of opposing pieces
                        for key, val in self.squares.items():
                            if val[1] != None and ((r+i,c+i) in add_legal_moves):
                                if val[1].notation == "Bb":
                                    if((r+i,c+i) in val[1].legal_moves) or ((r+i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c+i))
                                        break
                                if val[1].notation == "Rb":
                                    if((r+i,c+i) in val[1].legal_moves) or ((r+i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c+i))
                                        break
                                if val[1].notation == "Pb":
                                    # checking the diagonals of the black Pawn
                                    if((r+i,c+i) == (val[1].pos_r+1,val[1].pos_c-1)) or ((r+i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c+i))
                                        break
                                    if ((r+i,c+i) == (val[1].pos_r+1,val[1].pos_c+1)) or ((r+i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c+i))
                                        break
                                if val[1].notation == "Qb":
                                    if((r+i,c+i) in val[1].legal_moves) or ((r+i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c+i))
                                        break
                                if val[1].notation == "Nb":
                                    if((r+i,c+i) in val[1].legal_moves) or ((r+i,c+i) in val[1].defends):
                                        add_legal_moves.remove((r+i,c+i))
                                        break
                                if val[1].notation == "Kb":  
                                    if((r+i,c+i) in val[1].legal_moves) or ((r+i,c+i) in val[1].defends) or ((r+i,c+i) in val[1].border):
                                        add_legal_moves.remove((r+i,c+i))
                                        break
                    # ally piece to the diagonal bottom right
                    else:
                        # print("ALLY to the diagonal bottom right")

                        add_border.append((r+i,c+i))

                        add_defends.append((r+i,c+i))
                        i=2
                        break
                # no piece to the diagonal bottom right
                elif (self.squares[(r+i,c+i)][1] == None): 
                    add_border.append((r+i,c+i))

                    add_legal_moves.append((r+i,c+i))
                    # make sure king can't move to legal or attack spaces of opposing pieces
                    for key, val in self.squares.items():
                        if val[1] != None and ((r+i,c+i) in add_legal_moves):
                            if val[1].notation == "Bb":
                                if((r+i,c+i) in val[1].legal_moves) or ((r+i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c+i))
                                    break
                            if val[1].notation == "Rb":
                                if((r+i,c+i) in val[1].legal_moves):
                                    add_legal_moves.remove((r+i,c+i))
                                    break
                            if val[1].notation == "Pb":
                                # checking the diagonals of the black Pawn
                                if((r+i,c+i) == (val[1].pos_r+1,val[1].pos_c-1)) or ((r+i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c+i))
                                    break
                                if ((r+i,c+i) == (val[1].pos_r+1,val[1].pos_c+1)) or ((r+i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c+i))
                                    break
                            if val[1].notation == "Qb":
                                if((r+i,c+i) in val[1].legal_moves) or ((r+i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c+i))
                                    break
                            if val[1].notation == "Nb":
                                if((r+i,c+i) in val[1].legal_moves) or ((r+i,c+i) in val[1].defends):
                                    add_legal_moves.remove((r+i,c+i))
                                    break
                            if val[1].notation == "Kb":  
                                if((r+i,c+i) in val[1].legal_moves) or ((r+i,c+i) in val[1].defends) or ((r+i,c+i) in val[1].border):
                                    add_legal_moves.remove((r+i,c+i))
                                    break
            
            for i in range(c,c-2,-1):
                if i == c:
                    continue
                elif i < 0 or i > 7: 
                    i=c-2
                    break
                elif (self.squares[(r,i)][1] != None): 
                    add_border.append((r,i))

                    # enemy piece to the left
                    if (self.squares[(r,i)][1].color != actual_piece.color):
                        add_legal_moves.append((r,i))
                        # make sure king can't move to legal or attack spaces of opposing pieces
                        for key, val in self.squares.items():
                            if val[1] != None and ((r,i) in add_legal_moves):
                                if val[1].notation == "Bb":
                                    if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                if val[1].notation == "Rb":
                                    if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                if val[1].notation == "Pb":
                                    # checking the diagonals of the black Pawn
                                    if((r,i) == (val[1].pos_r+1,val[1].pos_c-1)) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                    if ((r,i) == (val[1].pos_r+1,val[1].pos_c+1)) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                if val[1].notation == "Qb":
                                    if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                if val[1].notation == "Nb":
                                    if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                if val[1].notation == "Kb":  
                                    if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends) or ((r,i) in val[1].border):
                                        add_legal_moves.remove((r,i))
                                        break
                    # ally piece to the left
                    else:
                        # print("ALLY to the left")

                        add_border.append((r,i))

                        add_defends.append((r,i))
                        i=c-2
                        break
                # no piece to the left
                elif (self.squares[(r,i)][1] == None): 
                    add_border.append((r,i))

                    add_legal_moves.append((r,i))
                    # make sure king can't move to legal or attack spaces of opposing pieces
                    for key, val in self.squares.items():
                        if val[1] != None and ((r,i) in add_legal_moves):
                            if val[1].notation == "Bb":
                                if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                            if val[1].notation == "Rb":
                                if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                            if val[1].notation == "Pb":
                                # checking the diagonals of the black Pawn
                                if((r,i) == (val[1].pos_r+1,val[1].pos_c-1)) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                                if ((r,i) == (val[1].pos_r+1,val[1].pos_c+1)) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                            if val[1].notation == "Qb":
                                if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                            if val[1].notation == "Nb":
                                if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                            if val[1].notation == "Kb":  
                                if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends) or ((r,i) in val[1].border):
                                    add_legal_moves.remove((r,i))
                                    break

            for i in range(c,c+2):
                if i == c:
                    continue
                elif i < 0 or i > 7: 
                    i=c+2
                    break
                elif (self.squares[(r,i)][1] != None): 
                    add_border.append((r,i))

                    # enemy piece to the right
                    if (self.squares[(r,i)][1].color != actual_piece.color):
                        add_legal_moves.append((r,i))
                        # make sure king can't move to legal or attack spaces of opposing pieces
                        for key, val in self.squares.items():
                            if val[1] != None and ((r,i) in add_legal_moves):                         
                                if val[1].notation == "Bb":
                                    if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                elif val[1].notation == "Rb":
                                    if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                elif val[1].notation == "Pb":
                                    # checking the diagonals of the black Pawn
                                    if((r,i) == (val[1].pos_r+1,val[1].pos_c-1)) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                    if ((r,i) == (val[1].pos_r+1,val[1].pos_c+1)) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                elif val[1].notation == "Qb":
                                    if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                elif val[1].notation == "Nb":
                                    if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                        add_legal_moves.remove((r,i))
                                        break
                                elif val[1].notation == "Kb":  
                                    if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends) or ((r,i) in val[1].border):
                                        add_legal_moves.remove((r,i))
                                        break
                    # ally piece to the right
                    else:
                        # print("ALLY to the right")

                        add_border.append((r,i))

                        add_defends.append((r,i))
                        i=c+2
                        break
                # no piece to the right
                elif (self.squares[(r,i)][1] == None): 
                    add_border.append((r,i))

                    add_legal_moves.append((r,i))
                    # make sure king can't move to legal or attack spaces of opposing pieces
                    for key, val in self.squares.items():
                        if val[1] != None and ((r,i) in add_legal_moves):
                            if val[1].notation == "Bb":
                                if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                            if val[1].notation == "Rb":
                                if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                            if val[1].notation == "Pb":
                                # checking the diagonals of the black Pawn
                                if((r,i) == (val[1].pos_r+1,val[1].pos_c-1)) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                                if((r,i) == (val[1].pos_r+1,val[1].pos_c+1)) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i)) 
                                    break
                            if val[1].notation == "Qb":
                                if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                            if val[1].notation == "Nb":
                                if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends):
                                    add_legal_moves.remove((r,i))
                                    break
                            if val[1].notation == "Kb":  
                                if((r,i) in val[1].legal_moves) or ((r,i) in val[1].defends) or ((r,i) in val[1].border):
                                    add_legal_moves.remove((r,i))
                                    break

            for i in range(r,r-2,-1):
                if i == r:
                    continue
                elif i < 0 or i > 7: 
                    i=r-2
                    break
                elif (self.squares[(i,c)][1] != None):
                    add_border.append((i,c))

                    # enemy piece above
                    if (self.squares[(i,c)][1].color != actual_piece.color):
                        add_legal_moves.append((i,c))
                        # make sure king can't move to legal or attack spaces of opposing pieces
                        for key, val in self.squares.items():
                            if val[1] != None and ((i,c) in add_legal_moves):
                                if val[1].notation == "Bb":
                                    if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                if val[1].notation == "Rb":
                                    if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                if val[1].notation == "Pb":
                                    # checking the diagonals of the black Pawn
                                    if((i,c) == (val[1].pos_r+1,val[1].pos_c-1)) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                    if ((i,c) == (val[1].pos_r+1,val[1].pos_c+1)) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                if val[1].notation == "Qb":
                                    if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                if val[1].notation == "Nb":
                                    if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                if val[1].notation == "Kb":  
                                    if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends) or ((i,c) in val[1].border):
                                        add_legal_moves.remove((i,c))
                                        break
                    # ally piece above
                    else:
                        # print("ALLY above")

                        add_border.append((i,c))

                        add_defends.append((i,c))
                        i=r-2
                        break
                # no piece above
                elif (self.squares[(i,c)][1] == None):
                    add_border.append((i,c))

                    add_legal_moves.append((i,c))
                    # make sure king can't move to legal or attack spaces of opposing pieces
                    for key, val in self.squares.items():
                        if val[1] != None and ((i,c) in add_legal_moves):
                            if val[1].notation == "Bb": 
                                if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                            if val[1].notation == "Rb":
                                if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                            if val[1].notation == "Pb":
                                # checking the diagonals of the black Pawn
                                if((i,c) == (val[1].pos_r+1,val[1].pos_c-1)) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                                if ((i,c) == (val[1].pos_r+1,val[1].pos_c+1)) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                            if val[1].notation == "Qb":
                                if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                            if val[1].notation == "Nb":
                                if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                            if val[1].notation == "Kb":  
                                if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends) or ((i,c) in val[1].border):
                                    add_legal_moves.remove((i,c))
                                    break

            for i in range(r,r+2):
                if i == r:
                    continue
                elif i < 0 or i > 7: 
                    i=r+2
                    break
                elif (self.squares[(i,c)][1] != None): 
                    add_border.append((i,c))

                    # enemy piece below
                    if (self.squares[(i,c)][1].color != actual_piece.color):
                        add_legal_moves.append((i,c))
                        # make sure king can't move to legal or attack spaces of opposing pieces
                        for key, val in self.squares.items():
                            if val[1] != None and ((i,c) in add_legal_moves):
                                if val[1].notation == "Bb":
                                    if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                if val[1].notation == "Rb":
                                    if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                if val[1].notation == "Pb":
                                    # checking the diagonals of the black Pawn
                                    if((i,c) == (val[1].pos_r+1,val[1].pos_c-1)) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                    if ((i,c) == (val[1].pos_r+1,val[1].pos_c+1)) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                if val[1].notation == "Qb":
                                    if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                if val[1].notation == "Nb":
                                    if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                        add_legal_moves.remove((i,c))
                                        break
                                if val[1].notation == "Kb":  
                                    if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends) or ((i,c) in val[1].border):
                                        add_legal_moves.remove((i,c))
                                        break
                    # ally piece below
                    else:
                        # print("ALLY below")

                        add_border.append((i,c))

                        add_defends.append((i,c))
                        i=r+2
                        break
                # no piece below
                elif (self.squares[(i,c)][1] == None):
                    add_border.append((i,c))

                    add_legal_moves.append((i,c))
                    # make sure king can't move to legal or attack spaces of opposing pieces
                    for key, val in self.squares.items():
                        if val[1] != None and ((i,c) in add_legal_moves):
                            if val[1].notation == "Bb":
                                if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                            if val[1].notation == "Rb":
                                if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                            if val[1].notation == "Pb":
                                # checking the diagonals of the black Pawn
                                if((i,c) == (val[1].pos_r+1,val[1].pos_c-1)) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                                if ((i,c) == (val[1].pos_r+1,val[1].pos_c+1)) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                            if val[1].notation == "Qb":
                                if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                            if val[1].notation == "Nb":
                                if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends):
                                    add_legal_moves.remove((i,c))
                                    break
                            if val[1].notation == "Kb":  
                                if((i,c) in val[1].legal_moves) or ((i,c) in val[1].defends) or ((i,c) in val[1].border):
                                    add_legal_moves.remove((i,c))
                                    break

            new_add_border = []
            for border in add_border:
                if border not in new_add_border:
                    new_add_border.append(border)

            actual_piece.defends = add_defends
            actual_piece.border = new_add_border
            return add_legal_moves
        #endregion

        #region QUEEN get legal moves
        if actual_piece.notation == "Q" or actual_piece.notation == "Qb":
            actual_piece.check_pathway = actual_piece.check_pathway if actual_piece.check_pathway != None else []
            actual_piece.pin_pathway = actual_piece.pin_pathway if actual_piece.pin_pathway != None else []

            add_legal_moves = []
            add_defends = []
            add_check_pathway = []

            add_pin_pathway = []
            pin2 = [] # will hold all values that are in the pathway of a possible pin if they second piece is a King then a pin has occurred
            
            for i in range(1,8):
                if r-i < 0 or c-i < 0:
                    i=8
                    break
                # no piece to the diagonal top left
                elif (self.squares[(r-i, c-i)][1] == None):
                    add_legal_moves.append((r-i,c-i))
                    add_check_pathway.append((r-i,c-i))
                # a piece to the diagonal top left that CAN be captured has been reached
                elif (self.squares[(r-i, c-i)][1] != None) and (self.squares[(r-i, c-i)][1].color != actual_piece.color):
                    if (self.squares[(r-i, c-i)][1].notation != "K") and (self.squares[(r-i, c-i)][1].notation != "Kb"):
                        pin2.append(self.squares[(r-i, c-i)][1].notation)
                        add_legal_moves.append((r-i, c-i))
                        
                        pinned_a_piece = False
                        for j in range(i+1,8):
                            if r-j < 0 or c-j < 0:
                                j=8
                                break
                            elif (self.squares[(r-j, c-j)][1] != None):
                                if (self.squares[(r-j, c-j)][1].color != actual_piece.color) and (self.squares[(r-j, c-j)][1].notation == "K" or self.squares[(r-j, c-j)][1].notation == "Kb"):
                                    pin2.append(self.squares[(r-j, c-j)][1].notation)
                                    if len(pin2) >= 2 and (pin2[1] == "K" or pin2[1] == "Kb"):
                                        pinned_a_piece = True
                                    j=8
                                    break
                                else:
                                    j=8
                                    break
                            else:
                                add_pin_pathway.append((r-j, c-j))
                        if pinned_a_piece:
                            self.squares[(r-i, c-i)][1].pinned = True
                            add_pin_pathway.extend(add_check_pathway)
                            actual_piece.pin_pathway.extend(add_pin_pathway)
                            # actual_piece.pin_pathway.append()
                            # self.squares[(r-i, c-i)][1].pin_pathway = add_pin_pathway
                        else:
                            self.squares[(r-i, c-i)][1].pinned = False

                        i=8
                        break
                    else:
                        add_legal_moves.append((r-i, c-i))
                        self.squares[(r-i, c-i)][1].in_check = True 
                        # # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")
                        actual_piece.check_pathway = [pos for pos in add_check_pathway]
                        i=8
                        break
                # a piece to the diagonal top left that is an ally has been reached
                elif (self.squares[(r-i, c-i)][1] != None) and (self.squares[(r-i, c-i)][1].color == actual_piece.color):
                    add_defends.append((r-i, c-i))
                    if self.squares[(r-i, c-i)][1].notation == "K" or self.squares[(r-i, c-i)][1].notation == "Kb":
                        add_defends.remove((r-i, c-i))
                    i=8
                    break
            add_check_pathway = []
            pin2 = []

            for i in range(1,8):
                if r+i > 7 or c-i < 0:
                    i=8
                    break
                # no piece to the diagonal bottom left
                elif (self.squares[(r+i, c-i)][1] == None): 
                    add_legal_moves.append((r+i,c-i))
                    add_check_pathway.append((r+i,c-i))
                # a piece to the diagonal bottom left that CAN be captured has been reached
                elif (self.squares[(r+i, c-i)][1] != None) and (self.squares[(r+i, c-i)][1].color != actual_piece.color):
                    if (self.squares[(r+i, c-i)][1].notation != "K") and (self.squares[(r+i, c-i)][1].notation != "Kb"):
                        pin2.append(self.squares[(r+i, c-i)][1].notation)
                        add_legal_moves.append((r+i, c-i))
                        
                        pinned_a_piece = False
                        for j in range(i+1,8):
                            if r+j > 7 or c-j < 0:
                                j=8
                                break
                            elif (self.squares[(r+j, c-j)][1] != None):
                                if (self.squares[(r+j, c-j)][1].color != actual_piece.color) and (self.squares[(r+j, c-j)][1].notation == "K" or self.squares[(r+j, c-j)][1].notation == "Kb"):
                                    pin2.append(self.squares[(r+j, c-j)][1].notation)
                                    if len(pin2) >= 2 and (pin2[1] == "K" or pin2[1] == "Kb"):
                                        pinned_a_piece = True
                                    j=8
                                    break
                                else:
                                    j=8
                                    break
                            else:
                                add_pin_pathway.append((r+j, c-j))
                        if pinned_a_piece:
                            self.squares[(r+i, c-i)][1].pinned = True
                            add_pin_pathway.extend(add_check_pathway)
                            actual_piece.pin_pathway.extend(add_pin_pathway)
                        else:
                            self.squares[(r+i, c-i)][1].pinned = False
                        
                        i=8
                        break
                    else:
                        add_legal_moves.append((r+i, c-i))
                        self.squares[(r+i, c-i)][1].in_check = True 
                        # # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")
                        actual_piece.check_pathway = [pos for pos in add_check_pathway]
                        i=8
                        break
                # a piece to the diagonal bottom left that is an ally has been reached
                elif (self.squares[(r+i, c-i)][1] != None) and (self.squares[(r+i, c-i)][1].color == actual_piece.color):
                    add_defends.append((r+i, c-i))
                    if self.squares[(r+i, c-i)][1].notation == "K" or self.squares[(r+i, c-i)][1].notation == "Kb":
                        add_defends.remove((r+i, c-i))
                    i=8
                    break
            add_check_pathway = []
            pin2 = []

            for i in range(1,8):
                if r-i < 0 or c+i > 7:
                    i=8
                    break
                # no piece to the diagonal top right
                elif (self.squares[(r-i, c+i)][1] == None): 
                    add_legal_moves.append((r-i, c+i))
                    add_check_pathway.append((r-i, c+i))
                # a piece to the diagonal top right that CAN be captured has been reached
                elif (self.squares[(r-i, c+i)][1] != None) and (self.squares[(r-i, c+i)][1].color != actual_piece.color):
                    if (self.squares[(r-i, c+i)][1].notation != "K") and (self.squares[(r-i, c+i)][1].notation != "Kb"):
                        pin2.append(self.squares[(r-i, c+i)][1].notation)
                        add_legal_moves.append((r-i, c+i))
                        
                        pinned_a_piece = False
                        for j in range(i+1,8):
                            if r-j < 0 or c+j > 7:
                                j=8
                                break
                            elif (self.squares[(r-j, c+j)][1] != None):
                                if (self.squares[(r-j, c+j)][1].color != actual_piece.color) and (self.squares[(r-j, c+j)][1].notation == "K" or self.squares[(r-j, c+j)][1].notation == "Kb"):
                                    pin2.append(self.squares[(r-j, c+j)][1].notation)
                                    if len(pin2) >= 2 and (pin2[1] == "K" or pin2[1] == "Kb"):
                                        pinned_a_piece = True
                                    j=8
                                    break
                                else:
                                    j=8
                                    break
                            else:
                                add_pin_pathway.append((r-j, c+j))
                        if pinned_a_piece:
                            self.squares[(r-i, c+i)][1].pinned = True
                            add_pin_pathway.extend(add_check_pathway)
                            actual_piece.pin_pathway.extend(add_pin_pathway)
                        else:
                            self.squares[(r-i, c+i)][1].pinned = False

                        i=8
                        break
                    else:
                        add_legal_moves.append((r-i, c+i))
                        self.squares[(r-i, c+i)][1].in_check = True 
                        # # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")
                        actual_piece.check_pathway = [pos for pos in add_check_pathway]
                        i=8
                        break
                # a piece to the diagonal top right that is an ally has been reached
                elif (self.squares[(r-i, c+i)][1] != None) and (self.squares[(r-i, c+i)][1].color == actual_piece.color):
                    add_defends.append((r-i, c+i))
                    if self.squares[(r-i, c+i)][1].notation == "K" or self.squares[(r-i, c+i)][1].notation == "Kb":
                            add_defends.remove((r-i, c+i))
                    i=8
                    break
            add_check_pathway = []
            pin2 = []

            for i in range(1,8):
                if r+i > 7 or c+i > 7: 
                    i=8
                    break
                # no piece to the diagonal bottom right
                elif (self.squares[(r+i, c+i)][1] == None): 
                    add_legal_moves.append((r+i, c+i))
                    add_check_pathway.append((r+i, c+i))
                # a piece to the diagonal bottom right that CAN be captured has been reached
                elif (self.squares[(r+i, c+i)][1] != None) and (self.squares[(r+i, c+i)][1].color != actual_piece.color):
                    if (self.squares[(r+i, c+i)][1].notation != "K") and (self.squares[(r+i, c+i)][1].notation != "Kb"):
                        pin2.append(self.squares[(r+i, c+i)][1].notation)
                        add_legal_moves.append((r+i, c+i))
                        
                        pinned_a_piece = False
                        for j in range(i+1,8):
                            if r+j > 7 or c+j > 7: 
                                j=8
                                break
                            elif (self.squares[(r+j, c+j)][1] != None):
                                if (self.squares[(r+j, c+j)][1].color != actual_piece.color) and (self.squares[(r+j, c+j)][1].notation == "K" or self.squares[(r+j, c+j)][1].notation == "Kb"):
                                    pin2.append(self.squares[(r+j, c+j)][1].notation)
                                    if len(pin2) >= 2 and (pin2[1] == "K" or pin2[1] == "Kb"):
                                        pinned_a_piece = True
                                    j=8
                                    break
                                else:
                                    j=8
                                    break
                            else:
                                add_pin_pathway.append((r+j, c+j))
                        if pinned_a_piece:
                            self.squares[(r+i, c+i)][1].pinned = True
                            add_pin_pathway.extend(add_check_pathway)
                            actual_piece.pin_pathway.extend(add_pin_pathway)
                        else:
                            self.squares[(r+i, c+i)][1].pinned = False
                        
                        i=8
                        break
                    else:
                        add_legal_moves.append((r+i, c+i))
                        self.squares[(r+i, c+i)][1].in_check = True 
                        # # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")
                        actual_piece.check_pathway = [pos for pos in add_check_pathway]
                        i=8
                        break
                # a piece to the diagonal bottom right that is an ally has been reached
                elif (self.squares[(r+i, c+i)][1] != None) and (self.squares[(r+i, c+i)][1].color == actual_piece.color):
                    add_defends.append((r+i, c+i))
                    if self.squares[(r+i, c+i)][1].notation == "K" or self.squares[(r+i, c+i)][1].notation == "Kb":
                        add_defends.remove((r+i, c+i))
                    i=8
                    break
            add_check_pathway = []
            pin2 = []
            
            for i in range(c,-1,-1):
                if i == c:
                    continue
                # no piece to the left
                if (self.squares[(r, i)][1] == None): 
                    add_legal_moves.append((r,i))
                    add_check_pathway.append((r,i))
                # a piece to the left that CAN be captured has been reached
                elif (self.squares[(r, i)][1] != None) and (self.squares[(r, i)][1].color != actual_piece.color):
                    if (self.squares[(r, i)][1].notation != "K") and (self.squares[(r, i)][1].notation != "Kb"):
                        pin2.append(self.squares[(r, i)][1].notation)
                        add_legal_moves.append((r,i))

                        pinned_a_piece = False
                        for j in range(i-1,-1,-1):
                            if j < 0: 
                                j=-1
                                break
                            elif (self.squares[(r, j)][1] != None):
                                if (self.squares[(r, j)][1].color != actual_piece.color) and (self.squares[(r, j)][1].notation == "K" or self.squares[(r, j)][1].notation == "Kb"):
                                    pin2.append(self.squares[(r, j)][1].notation)
                                    if len(pin2) >= 2 and (pin2[1] == "K" or pin2[1] == "Kb"):
                                        pinned_a_piece = True
                                    j=-1
                                    break
                                else:
                                    j=-1
                                    break
                            else:
                                add_pin_pathway.append((r, j))
                        if pinned_a_piece:
                            self.squares[(r, i)][1].pinned = True
                            add_pin_pathway.extend(add_check_pathway)
                            actual_piece.pin_pathway.extend(add_pin_pathway)
                        else:
                            self.squares[(r, i)][1].pinned = False

                        i=-1
                        break
                    else:
                        add_legal_moves.append((r,i))
                        self.squares[(r, i)][1].in_check = True 
                        # # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")
                        actual_piece.check_pathway = [pos for pos in add_check_pathway]
                        i=-1
                        break
                # a piece to the left that is an ally has been reached
                elif (self.squares[(r, i)][1] != None) and (self.squares[(r, i)][1].color == actual_piece.color):
                    add_defends.append((r,i))
                    if self.squares[(r, i)][1].notation == "K" or self.squares[(r, i)][1].notation == "Kb":
                        add_defends.remove((r,i))
                    i=-1
                    break
            add_check_pathway = []
            pin2 = []

            for i in range(c,8):
                if i == c:
                    continue
                # no piece to the right
                if (self.squares[(r, i)][1] == None): 
                    add_legal_moves.append((r,i))
                    add_check_pathway.append((r,i))
                # a piece to the right that CAN be captured has been reached
                elif (self.squares[(r, i)][1] != None) and (self.squares[(r, i)][1].color != actual_piece.color):
                    if (self.squares[(r, i)][1].notation != "K") and (self.squares[(r, i)][1].notation != "Kb"):
                        pin2.append(self.squares[(r, i)][1].notation)
                        add_legal_moves.append((r,i))

                        pinned_a_piece = False
                        for j in range(i+1,8):
                            if j > 7:
                                j=8
                                break
                            elif (self.squares[(r, j)][1] != None):
                                if (self.squares[(r, j)][1].color != actual_piece.color) and (self.squares[(r, j)][1].notation == "K" or self.squares[(r, j)][1].notation == "Kb"):
                                    pin2.append(self.squares[(r, j)][1].notation)
                                    if len(pin2) >= 2 and (pin2[1] == "K" or pin2[1] == "Kb"):
                                        pinned_a_piece = True
                                    j=8
                                    break
                                else:
                                    j=8
                                    break
                            else:
                                add_pin_pathway.append((r, j))
                        if pinned_a_piece:
                            self.squares[(r, i)][1].pinned = True
                            add_pin_pathway.extend(add_check_pathway)
                            actual_piece.pin_pathway.extend(add_pin_pathway)
                        else:
                            self.squares[(r, i)][1].pinned = False

                        i=8
                        break
                    else:
                        add_legal_moves.append((r,i))
                        self.squares[(r, i)][1].in_check = True 
                        # # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")
                        actual_piece.check_pathway = [pos for pos in add_check_pathway]
                        i=8
                        break
                # a piece to the right that is an ally has been reached
                elif (self.squares[(r, i)][1] != None) and (self.squares[(r, i)][1].color == actual_piece.color):
                    add_defends.append((r,i))
                    if self.squares[(r, i)][1].notation == "K" or self.squares[(r, i)][1].notation == "Kb":
                        add_defends.remove((r,i))
                    i=8
                    break
            add_check_pathway = []
            pin2 = []

            for i in range(r,-1,-1):
                if i == r:
                    continue
                # no piece above
                if (self.squares[(i, c)][1] == None): 
                    add_legal_moves.append((i,c))
                    add_check_pathway.append((i,c))
                # a piece to above that CAN be captured has been reached
                elif (self.squares[(i, c)][1] != None) and (self.squares[(i, c)][1].color != actual_piece.color):
                    if (self.squares[(i, c)][1].notation != "K") and (self.squares[(i, c)][1].notation != "Kb"):
                        pin2.append(self.squares[(i, c)][1].notation)
                        add_legal_moves.append((i,c))

                        pinned_a_piece = False
                        for j in range(i-1,-1,-1):
                            if j < 0:
                                j=-1
                                break
                            elif (self.squares[(j, c)][1] != None):
                                if (self.squares[(j, c)][1].color != actual_piece.color) and (self.squares[(j, c)][1].notation == "K" or self.squares[(j, c)][1].notation == "Kb"):
                                    pin2.append(self.squares[(j, c)][1].notation)
                                    if len(pin2) >= 2 and (pin2[1] == "K" or pin2[1] == "Kb"):
                                        pinned_a_piece = True
                                    j=-1
                                    break
                                else:
                                    j=-1
                                    break
                            else:
                                add_pin_pathway.append((j, c))
                        if pinned_a_piece:
                            self.squares[(i, c)][1].pinned = True
                            add_pin_pathway.extend(add_check_pathway)
                            actual_piece.pin_pathway.extend(add_pin_pathway)
                        else:
                            self.squares[(i, c)][1].pinned = False

                        i=-1
                        break
                    else:
                        add_legal_moves.append((i,c))
                        self.squares[(i, c)][1].in_check = True 
                        # # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")
                        actual_piece.check_pathway = [pos for pos in add_check_pathway]
                        i=-1
                        break
                # a piece above that is an ally has been reached
                elif (self.squares[(i, c)][1] != None) and (self.squares[(i, c)][1].color == actual_piece.color):
                    add_defends.append((i,c))
                    if self.squares[(i, c)][1].notation == "K" or self.squares[(i, c)][1].notation == "Kb":
                        add_defends.remove((i,c))
                    i=-1
                    break
            add_check_pathway = []
            pin2 = []

            for i in range(r,8):
                if i == r:
                    continue
                # no piece below
                if (self.squares[(i, c)][1] == None): 
                    add_legal_moves.append((i,c))
                    add_check_pathway.append((i,c))
                # a piece below that CAN be captured has been reached
                elif (self.squares[(i, c)][1] != None) and (self.squares[(i, c)][1].color != actual_piece.color):
                    if (self.squares[(i, c)][1].notation != "K") and (self.squares[(i, c)][1].notation != "Kb"):
                        pin2.append(self.squares[(i, c)][1].notation)
                        add_legal_moves.append((i,c))

                        pinned_a_piece = False
                        for j in range(i+1,8):
                            if j > 7:
                                j=8
                                break
                            elif (self.squares[(j, c)][1] != None):
                                if (self.squares[(j, c)][1].color != actual_piece.color) and (self.squares[(j, c)][1].notation == "K" or self.squares[(j, c)][1].notation == "Kb"):
                                    pin2.append(self.squares[(j, c)][1].notation)
                                    if len(pin2) >= 2 and (pin2[1] == "K" or pin2[1] == "Kb"):
                                        pinned_a_piece = True
                                    j=8
                                    break
                                else:
                                    j=8
                                    break
                            else:
                                add_pin_pathway.append((j, c))
                        if pinned_a_piece:
                            self.squares[(i, c)][1].pinned = True
                            add_pin_pathway.extend(add_check_pathway)
                            actual_piece.pin_pathway.extend(add_pin_pathway)
                        else:
                            self.squares[(i, c)][1].pinned = False

                        i=8
                        break
                    else:
                        add_legal_moves.append((i,c))
                        self.squares[(i, c)][1].in_check = True 
                        # # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")
                        actual_piece.check_pathway = [pos for pos in add_check_pathway]
                        i=8
                        break
                # a piece below that is an ally has been reached
                elif (self.squares[(i, c)][1] != None) and (self.squares[(i, c)][1].color == actual_piece.color):
                    add_defends.append((i,c))
                    if self.squares[(i, c)][1].notation == "K" or self.squares[(i, c)][1].notation == "Kb":
                        add_defends.remove((i,c))
                    i=8
                    break
            add_check_pathway = []

            actual_piece.defends = add_defends
            return add_legal_moves
        #endregion
        
        #region BISHOP get legal moves
        if actual_piece.notation == "B" or actual_piece.notation == "Bb":
            actual_piece.check_pathway = actual_piece.check_pathway if actual_piece.check_pathway != None else []
            actual_piece.pin_pathway = actual_piece.pin_pathway if actual_piece.pin_pathway != None else []

            add_legal_moves = []
            add_defends = []
            add_check_pathway = []
            add_pin_pathway = []
            pin2 = []
            
            for i in range(1,8):
                if r-i < 0 or c-i < 0:
                    i=8
                    break
                # no piece to the diagonal top left
                elif (self.squares[(r-i, c-i)][1] == None): 
                    add_legal_moves.append((r-i,c-i))
                    add_check_pathway.append((r-i,c-i))
                # a piece to the diagonal top left that CAN be captured has been reached
                elif (self.squares[(r-i, c-i)][1] != None) and (self.squares[(r-i, c-i)][1].color != actual_piece.color):
                    if (self.squares[(r-i, c-i)][1].notation != "K") and (self.squares[(r-i, c-i)][1].notation != "Kb"):
                        pin2.append(self.squares[(r-i, c-i)][1].notation)
                        add_legal_moves.append((r-i, c-i))

                        pinned_a_piece = False
                        for j in range(i+1,8):
                            if r-j < 0 or c-j < 0:
                                j=8
                                break
                            elif (self.squares[(r-j, c-j)][1] != None):
                                if (self.squares[(r-j, c-j)][1].color != actual_piece.color) and (self.squares[(r-j, c-j)][1].notation == "K" or self.squares[(r-j, c-j)][1].notation == "Kb"):
                                    pin2.append(self.squares[(r-j, c-j)][1].notation)
                                    if len(pin2) >= 2 and (pin2[1] == "K" or pin2[1] == "Kb"):
                                        pinned_a_piece = True
                                    j=8
                                    break
                                else:
                                    j=8
                                    break
                            else:
                                add_pin_pathway.append((r-j, c-j))
                        if pinned_a_piece:
                            self.squares[(r-i, c-i)][1].pinned = True
                            add_pin_pathway.extend(add_check_pathway)
                            actual_piece.pin_pathway.extend(add_pin_pathway)
                        else:
                            self.squares[(r-i, c-i)][1].pinned = False

                        i=8
                        break
                    else:
                        add_legal_moves.append((r-i, c-i))
                        self.squares[(r-i, c-i)][1].in_check = True 
                        # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")
                        actual_piece.check_pathway = [pos for pos in add_check_pathway]
                        i=8
                        break
                # a piece to the diagonal top left that is an ally has been reached
                elif (self.squares[(r-i, c-i)][1] != None) and (self.squares[(r-i, c-i)][1].color == actual_piece.color):
                    add_defends.append((r-i, c-i))
                    if self.squares[(r-i, c-i)][1].notation == "K" or self.squares[(r-i, c-i)][1].notation == "Kb":
                        add_defends.remove((r-i, c-i))
                    i=8
                    break
            add_check_pathway = []
            pin2 = []
            
            for i in range(1,8):
                if r+i > 7 or c-i < 0:
                    i=8
                    break
                # no piece to the diagonal bottom left
                elif (self.squares[(r+i, c-i)][1] == None): 
                    add_legal_moves.append((r+i,c-i))
                    add_check_pathway.append((r+i,c-i))
                # a piece to the diagonal bottom left that CAN be captured has been reached
                elif (self.squares[(r+i, c-i)][1] != None) and (self.squares[(r+i, c-i)][1].color != actual_piece.color):
                    if (self.squares[(r+i, c-i)][1].notation != "K") and (self.squares[(r+i, c-i)][1].notation != "Kb"):
                        pin2.append(self.squares[(r+i, c-i)][1].notation)
                        add_legal_moves.append((r+i, c-i))

                        pinned_a_piece = False
                        for j in range(i+1,8):
                            if r+j > 7 or c-j < 0:
                                j=8
                                break
                            elif (self.squares[(r+j, c-j)][1] != None):
                                if (self.squares[(r+j, c-j)][1].color != actual_piece.color) and (self.squares[(r+j, c-j)][1].notation == "K" or self.squares[(r+j, c-j)][1].notation == "Kb"):
                                    pin2.append(self.squares[(r+j, c-j)][1].notation)
                                    if len(pin2) >= 2 and (pin2[1] == "K" or pin2[1] == "Kb"):
                                        pinned_a_piece = True
                                    j=8
                                    break
                                else:
                                    j=8
                                    break
                            else:
                                add_pin_pathway.append((r+j, c-j))
                        if pinned_a_piece:
                            self.squares[(r+i, c-i)][1].pinned = True
                            add_pin_pathway.extend(add_check_pathway)
                            actual_piece.pin_pathway.extend(add_pin_pathway)
                        else:
                            self.squares[(r+i, c-i)][1].pinned = False

                        i=8
                        break
                    else:
                        add_legal_moves.append((r+i, c-i))
                        self.squares[(r+i, c-i)][1].in_check = True 
                        # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")
                        actual_piece.check_pathway = [pos for pos in add_check_pathway]
                        i=8
                        break
                # a piece to the diagonal bottom left that is an ally has been reached
                elif (self.squares[(r+i, c-i)][1] != None) and (self.squares[(r+i, c-i)][1].color == actual_piece.color):
                    add_defends.append((r+i, c-i))
                    if self.squares[(r+i, c-i)][1].notation == "K" or self.squares[(r+i, c-i)][1].notation == "Kb":
                        add_defends.remove((r+i, c-i))
                    i=8
                    break
            add_check_pathway = []
            pin2 = []

            for i in range(1,8):
                if r-i < 0 or c+i > 7:
                    i=8
                    break
                # no piece to the diagonal top right
                elif (self.squares[(r-i, c+i)][1] == None): 
                    add_legal_moves.append((r-i, c+i))
                    add_check_pathway.append((r-i, c+i))
                # a piece to the diagonal top right that CAN be captured has been reached
                elif (self.squares[(r-i, c+i)][1] != None) and (self.squares[(r-i, c+i)][1].color != actual_piece.color):
                    if (self.squares[(r-i, c+i)][1].notation != "K") and (self.squares[(r-i, c+i)][1].notation != "Kb"):
                        pin2.append(self.squares[(r-i, c+i)][1].notation)
                        add_legal_moves.append((r-i, c+i))

                        pinned_a_piece = False
                        for j in range(i+1,8):
                            if r-j < 0 or c+j > 7:
                                j=8
                                break
                            elif (self.squares[(r-j, c+j)][1] != None):
                                if (self.squares[(r-j, c+j)][1].color != actual_piece.color) and (self.squares[(r-j, c+j)][1].notation == "K" or self.squares[(r-j, c+j)][1].notation == "Kb"):
                                    pin2.append(self.squares[(r-j, c+j)][1].notation)
                                    if len(pin2) >= 2 and (pin2[1] == "K" or pin2[1] == "Kb"):
                                        pinned_a_piece = True
                                    j=8
                                    break
                                else:
                                    j=8
                                    break
                            else:
                                add_pin_pathway.append((r-j, c+j))

                        if pinned_a_piece:
                            self.squares[(r-i, c+i)][1].pinned = True
                            add_pin_pathway.extend(add_check_pathway)
                            actual_piece.pin_pathway.extend(add_pin_pathway)
                            # self.squares[(r-i, c+i)][1].pin_pathway = add_pin_pathway

                            # print("ADDING check path", add_check_pathway)
                            # print(actual_piece.pin_pathway)
                            
                            # print(f"I the {self.squares[(r-i, c+i)][1].color} {self.squares[(r-i, c+i)][1].notation} am pinned")
                            # print("Bishop's pin pathway:", actual_piece.pin_pathway)
                            # print("BISHOP top right diag attack")
                        else:
                            self.squares[(r-i, c+i)][1].pinned = False

                        i=-8
                        break
                    else:
                        add_legal_moves.append((r-i, c+i))
                        self.squares[(r-i, c+i)][1].in_check = True 
                        # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")
                        actual_piece.check_pathway = [pos for pos in add_check_pathway]
                        i=-8
                        break
                # a piece to the diagonal top right that is an ally has been reached
                elif (self.squares[(r-i, c+i)][1] != None) and (self.squares[(r-i, c+i)][1].color == actual_piece.color):
                    add_defends.append((r-i, c+i))
                    if self.squares[(r-i, c+i)][1].notation == "K" or self.squares[(r-i, c+i)][1].notation == "Kb":
                        add_defends.remove((r-i, c+i))
                    i=-8
                    break
            add_check_pathway = []

            for i in range(1,8):
                if r+i > 7 or c+i > 7:
                    i=8
                    break
                # no piece to the diagonal bottom right
                elif (self.squares[(r+i, c+i)][1] == None): 
                    add_legal_moves.append((r+i, c+i))
                    add_check_pathway.append((r+i, c+i))
                # a piece to the diagonal bottom right that CAN be captured has been reached
                elif (self.squares[(r+i, c+i)][1] != None) and (self.squares[(r+i, c+i)][1].color != actual_piece.color):
                    if (self.squares[(r+i, c+i)][1].notation != "K") and (self.squares[(r+i, c+i)][1].notation != "Kb"):
                        pin2.append(self.squares[(r+i, c+i)][1].notation)
                        add_legal_moves.append((r+i, c+i))

                        pinned_a_piece = False
                        for j in range(i+1,8):
                            if r+j > 7 or c+j > 7:
                                j=8
                                break
                            elif (self.squares[(r+j, c+j)][1] != None):
                                if (self.squares[(r+j, c+j)][1].color != actual_piece.color) and (self.squares[(r+j, c+j)][1].notation == "K" or self.squares[(r+j, c+j)][1].notation == "Kb"):
                                    pin2.append(self.squares[(r+j, c+j)][1].notation)
                                    if len(pin2) >= 2 and (pin2[1] == "K" or pin2[1] == "Kb"):
                                        pinned_a_piece = True
                                    j=8
                                    break
                                else:
                                    j=8
                                    break
                            else:
                                add_pin_pathway.append((r+j, c+j))
                        if pinned_a_piece:
                            self.squares[(r+i, c+i)][1].pinned = True
                            add_pin_pathway.extend(add_check_pathway)
                            actual_piece.pin_pathway.extend(add_pin_pathway)
                        else:
                            self.squares[(r+i, c+i)][1].pinned = False

                        i=8
                        break
                    else:
                        add_legal_moves.append((r+i, c+i))
                        self.squares[(r+i, c+i)][1].in_check = True 
                        # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")
                        actual_piece.check_pathway = [pos for pos in add_check_pathway]
                        i=8
                        break
                # a piece to the diagonal bottom right that is an ally has been reached
                elif (self.squares[(r+i, c+i)][1] != None) and (self.squares[(r+i, c+i)][1].color == actual_piece.color):
                    add_defends.append((r+i, c+i))
                    if self.squares[(r+i, c+i)][1].notation == "K" or self.squares[(r+i, c+i)][1].notation == "Kb":
                        add_defends.remove((r+i, c+i))
                    i=8
                    break
            add_check_pathway = []

            actual_piece.defends = add_defends
            return add_legal_moves
        #endregion

        #region KNIGHT get legal moves
        if actual_piece.notation == "N" or actual_piece.notation == "Nb":
            add_legal_moves = []
            add_defends = []

            for key, val in self.squares.items():
                if (val[1] != None): # there is a piece at the current square
                    if val[1].color != actual_piece.color:
                        # top left is enemy
                        if (val[1].pos_r == r-2) and (val[1].pos_c == c-1) and (val[1].notation != "K") and (val[1].notation != "Kb"):
                            add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                        elif (val[1].pos_r == r-2) and (val[1].pos_c == c-1) and (val[1].notation == "K" or val[1].notation == "Kb"):
                            add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                            val[1].in_check = True 
                            # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")

                        # top right is empty
                        if (val[1].pos_r == r-2) and (val[1].pos_c == c+1) and (val[1].notation != "K") and (val[1].notation != "Kb"):
                            add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                        elif (val[1].pos_r == r-2) and (val[1].pos_c == c+1) and (val[1].notation == "K" or val[1].notation == "Kb"):
                            add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                            val[1].in_check = True 
                            # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")

                        # left top is enemy
                        if (val[1].pos_r == r-1) and (val[1].pos_c == c-2) and (val[1].notation != "K") and (val[1].notation != "Kb"):
                            add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                        elif (val[1].pos_r == r-1) and (val[1].pos_c == c-2) and (val[1].notation == "K" or val[1].notation == "Kb"):
                            add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                            val[1].in_check = True 
                            # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")
                            
                        # left bottom is enemy
                        if (val[1].pos_r == r+1) and (val[1].pos_c == c-2) and (val[1].notation != "K") and (val[1].notation != "Kb"):
                            add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                        elif (val[1].pos_r == r+1) and (val[1].pos_c == c-2) and (val[1].notation == "K" or val[1].notation == "Kb"):
                            add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                            val[1].in_check = True 
                            # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")

                        # bottom left is enemy
                        if (val[1].pos_r == r+2) and (val[1].pos_c == c-1) and (val[1].notation != "K") and (val[1].notation != "Kb"):
                            add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                        elif (val[1].pos_r == r+2) and (val[1].pos_c == c-1) and (val[1].notation == "K" or val[1].notation == "Kb"):
                            add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                            val[1].in_check = True 
                            # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")

                        # bottom right is enemy
                        if (val[1].pos_r == r+2) and (val[1].pos_c == c+1) and (val[1].notation != "K") and (val[1].notation != "Kb"):
                            add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                        elif (val[1].pos_r == r+2) and (val[1].pos_c == c+1) and (val[1].notation == "K" or val[1].notation == "Kb"):
                            add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                            val[1].in_check = True 
                            # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")

                        # right top is enemy
                        if (val[1].pos_r == r-1) and (val[1].pos_c == c+2) and (val[1].notation != "K") and (val[1].notation != "Kb"):
                            add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                        elif (val[1].pos_r == r-1) and (val[1].pos_c == c+2) and (val[1].notation == "K" or val[1].notation == "Kb"):
                            add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                            val[1].in_check = True 
                            # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")

                        # right bottom is enemy
                        if (val[1].pos_r == r+1) and (val[1].pos_c == c+2) and (val[1].notation != "K") and (val[1].notation != "Kb"):
                            add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                        elif (val[1].pos_r == r+1) and (val[1].pos_c == c+2) and (val[1].notation == "K" or val[1].notation == "Kb"):
                            add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                            val[1].in_check = True 
                            # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")

                    else:
                        # top left is ally
                        if (val[1].pos_r == r-2) and (val[1].pos_c == c-1) and (val[1].notation != "K" and val[1].notation != "Kb"):
                            add_defends.append((val[1].pos_r, val[1].pos_c))
                        # top right is ally
                        if (val[1].pos_r == r-2) and (val[1].pos_c == c+1) and (val[1].notation != "K" and val[1].notation != "Kb"):
                            add_defends.append((val[1].pos_r, val[1].pos_c))
                        
                        # left top is ally
                        if (val[1].pos_r == r-1) and (val[1].pos_c == c-2) and (val[1].notation != "K" and val[1].notation != "Kb"):
                            add_defends.append((val[1].pos_r, val[1].pos_c))
                        # left bottom is ally
                        if (val[1].pos_r == r+1) and (val[1].pos_c == c-2) and (val[1].notation != "K" and val[1].notation != "Kb"):
                            add_defends.append((val[1].pos_r, val[1].pos_c))

                        # bottom left is ally
                        if (val[1].pos_r == r+2) and (val[1].pos_c == c-1) and (val[1].notation != "K" and val[1].notation != "Kb"):
                            add_defends.append((val[1].pos_r, val[1].pos_c))
                        # bottom right is ally
                        if (val[1].pos_r == r+2) and (val[1].pos_c == c+1) and (val[1].notation != "K" and val[1].notation != "Kb"):
                            add_defends.append((val[1].pos_r, val[1].pos_c))

                        # right top is ally
                        if (val[1].pos_r == r-1) and (val[1].pos_c == c+2) and (val[1].notation != "K" and val[1].notation != "Kb"):
                            add_defends.append((val[1].pos_r, val[1].pos_c))
                        # right bottom is ally
                        if (val[1].pos_r == r+1) and (val[1].pos_c == c+2) and (val[1].notation != "K" and val[1].notation != "Kb"):
                            add_defends.append((val[1].pos_r, val[1].pos_c))
                else:
                    # top left is empty
                    if (key[0] == r-2) and (key[1] == c-1):
                        add_legal_moves.append((key[0], key[1]))
                    # top right is empty
                    if (key[0] == r-2) and (key[1] == c+1):
                        add_legal_moves.append((key[0], key[1]))
                    
                    # left top is empty
                    if (key[0] == r-1) and (key[1] == c-2):
                        add_legal_moves.append((key[0], key[1]))
                    # left bottom is empty
                    if (key[0] == r+1) and (key[1] == c-2):
                        add_legal_moves.append((key[0], key[1]))

                    # bottom left is empty
                    if (key[0] == r+2) and (key[1] == c-1):
                        add_legal_moves.append((key[0], key[1]))
                    # bottom right is empty
                    if (key[0] == r+2) and (key[1] == c+1):
                        add_legal_moves.append((key[0], key[1]))

                    # right top is empty
                    if (key[0] == r-1) and (key[1] == c+2):
                        add_legal_moves.append((key[0], key[1]))
                    # right bottom is empty
                    if (key[0] == r+1) and (key[1] == c+2):
                        add_legal_moves.append((key[0], key[1]))

            actual_piece.defends = add_defends
            return add_legal_moves
        #endregion

        #region ROOK get legal moves
        if actual_piece.notation == "R" or actual_piece.notation == "Rb":
            actual_piece.check_pathway = actual_piece.check_pathway if actual_piece.check_pathway != None else []
            actual_piece.pin_pathway = actual_piece.pin_pathway if actual_piece.pin_pathway != None else []

            add_legal_moves = []
            add_defends = []
            add_check_pathway = []
            add_pin_pathway = []
            pin2 = []
            
            for i in range(c,-1,-1):
                if i == c:
                    continue
                # no piece to the left
                if (self.squares[(r, i)][1] == None): 
                    add_legal_moves.append((r,i))
                    add_check_pathway.append((r,i))
                # a piece to the left that CAN be captured has been reached
                elif (self.squares[(r, i)][1] != None) and (self.squares[(r, i)][1].color != actual_piece.color):
                    if (self.squares[(r, i)][1].notation != "K") and (self.squares[(r, i)][1].notation != "Kb"):
                        pin2.append(self.squares[(r, i)][1].notation)
                        add_legal_moves.append((r,i))

                        unpins = [] # an array of actual pieces that will have their pinned attribute set to False
                        self.squares[(r, i)][1].pinned = False
                        pinned_a_piece = False
                        for j in range(i-1,-1,-1):
                            if j < 0:
                                j=-1
                                break
                            elif (self.squares[(r, j)][1] != None):
                                if (self.squares[(r, j)][1].color != actual_piece.color) and (self.squares[(r, j)][1].notation == "K" or self.squares[(r, j)][1].notation == "Kb"):
                                    pin2.append(self.squares[(r, j)][1].notation)
                                    if len(pin2) >= 2 and (pin2[1] == "K" or pin2[1] == "Kb"):
                                        pinned_a_piece = True
                                    j=-1
                                    break
                                else:
                                    unpins.append(self.squares[(r, j)][1]) # appending the 2nd enemy piece since it shouldn't be pinned anymore
                                    j=-1
                                    break
                            else:
                                add_pin_pathway.append((r, j))
                        if pinned_a_piece:
                            self.squares[(r, i)][1].pinned = True
                            add_pin_pathway.extend(add_check_pathway)
                            actual_piece.pin_pathway.extend(add_pin_pathway)
                        else:
                            for piece in unpins:
                                print('Piece Being Unpinned:',piece.notation)
                                piece.pinned = False
                                piece.legal_moves = self.get_legal_moves(piece, piece.pos_r, piece.pos_c)
                            self.squares[(r, i)][1].pinned = False

                        i=-1
                        break
                    else:
                        add_legal_moves.append((r,i))
                        self.squares[(r, i)][1].in_check = True 
                        # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")
                        actual_piece.check_pathway = [pos for pos in add_check_pathway]
                        i=-1
                        break
                # a piece to the left that is an ally has been reached
                elif (self.squares[(r, i)][1] != None) and (self.squares[(r, i)][1].color == actual_piece.color):
                    add_defends.append((r,i))
                    if self.squares[(r, i)][1].notation == "K" or self.squares[(r, i)][1].notation == "Kb":
                        add_defends.remove((r,i))
                    i=-1
                    break
            add_check_pathway = []
            pin2 = []

            for i in range(c,8):
                if i == c:
                    continue
                # no piece to the right
                if (self.squares[(r, i)][1] == None): 
                    add_legal_moves.append((r,i))
                    add_check_pathway.append((r,i))
                # a piece to the right that CAN be captured has been reached
                elif (self.squares[(r, i)][1] != None) and (self.squares[(r, i)][1].color != actual_piece.color):
                    if (self.squares[(r, i)][1].notation != "K") and (self.squares[(r, i)][1].notation != "Kb"):
                        pin2.append(self.squares[(r, i)][1].notation)
                        add_legal_moves.append((r,i))

                        pinned_a_piece = False
                        for j in range(i+1,8):
                            if j > 7:
                                j=8
                                break
                            elif (self.squares[(r, j)][1] != None):
                                if (self.squares[(r, j)][1].color != actual_piece.color) and (self.squares[(r, j)][1].notation == "K" or self.squares[(r, j)][1].notation == "Kb"):
                                    pin2.append(self.squares[(r, j)][1].notation)
                                    if len(pin2) >= 2 and (pin2[1] == "K" or pin2[1] == "Kb"):
                                        pinned_a_piece = True
                                    j=8
                                    break
                                else:
                                    j=8
                                    break
                            else:
                                add_pin_pathway.append((r, j))
                        if pinned_a_piece:
                            self.squares[(r, i)][1].pinned = True
                            add_pin_pathway.extend(add_check_pathway)
                            actual_piece.pin_pathway.extend(add_pin_pathway)
                        else:
                            self.squares[(r, i)][1].pinned = False

                        i=-1
                        break
                    else:
                        add_legal_moves.append((r,i))
                        self.squares[(r, i)][1].in_check = True 
                        # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")
                        actual_piece.check_pathway = [pos for pos in add_check_pathway]
                        i=-1
                        break
                # a piece to the right that is an ally has been reached
                elif (self.squares[(r, i)][1] != None) and (self.squares[(r, i)][1].color == actual_piece.color):
                    add_defends.append((r,i))
                    if self.squares[(r, i)][1].notation == "K" or self.squares[(r, i)][1].notation == "Kb":
                        add_defends.remove((r,i))
                    i=-1
                    break
            add_check_pathway = []
            pin2 = []

            for i in range(r,-1,-1):
                if i == r:
                    continue
                # no piece above
                if (self.squares[(i, c)][1] == None): 
                    add_legal_moves.append((i,c))
                    add_check_pathway.append((i,c))
                # a piece to above that CAN be captured has been reached
                elif (self.squares[(i, c)][1] != None) and (self.squares[(i, c)][1].color != actual_piece.color):
                    if (self.squares[(i, c)][1].notation != "K") and (self.squares[(i, c)][1].notation != "Kb"):
                        pin2.append(self.squares[(i, c)][1].notation)
                        add_legal_moves.append((i,c))

                        unpins = [] # an array of actual pieces that will have their pinned attribute set to False
                        self.squares[(i, c)][1].pinned = False
                        pinned_a_piece = False
                        for j in range(i-1,-1,-1):
                            if j < 0:
                                j=-1
                                break
                            elif (self.squares[(j, c)][1] != None):
                                if (self.squares[(j, c)][1].color != actual_piece.color) and (self.squares[(j, c)][1].notation == "K" or self.squares[(j, c)][1].notation == "Kb"):
                                    pin2.append(self.squares[(j, c)][1].notation)
                                    if len(pin2) >= 2 and (pin2[1] == "K" or pin2[1] == "Kb"):
                                        pinned_a_piece = True
                                    j=-1
                                    break
                                else:
                                    unpins.append(self.squares[(j, c)][1]) # appending the 2nd enemy piece since it shouldn't be pinned anymore
                                    j=-1
                                    break
                            else:
                                add_pin_pathway.append((j, c))
                        if pinned_a_piece:
                            self.squares[(i, c)][1].pinned = True
                            add_pin_pathway.extend(add_check_pathway)
                            actual_piece.pin_pathway.extend(add_pin_pathway)
                        else:
                            for piece in unpins:
                                print('Piece Being Unpinned:', piece.notation)
                                piece.pinned = False
                                piece.legal_moves = self.get_legal_moves(piece, piece.pos_r, piece.pos_c)
                            self.squares[(i, c)][1].pinned = False

                        i=-1
                        break
                    else:
                        add_legal_moves.append((i,c))
                        self.squares[(i, c)][1].in_check = True 
                        # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")
                        actual_piece.check_pathway = [pos for pos in add_check_pathway]
                        i=-1
                        break
                # a piece above that is an ally has been reached
                elif (self.squares[(i, c)][1] != None) and (self.squares[(i, c)][1].color == actual_piece.color):
                    add_defends.append((i,c))
                    if self.squares[(i, c)][1].notation == "K" or self.squares[(i, c)][1].notation == "Kb":
                        add_defends.remove((i,c))
                    i=-1
                    break
            add_check_pathway = []
            pin2 = []

            for i in range(r,8):
                if i == r:
                    continue
                # no piece below
                if (self.squares[(i, c)][1] == None): 
                    add_legal_moves.append((i,c))
                    add_check_pathway.append((i,c))
                # a piece below that CAN be captured has been reached
                elif (self.squares[(i, c)][1] != None) and (self.squares[(i, c)][1].color != actual_piece.color):
                    if (self.squares[(i, c)][1].notation != "K") and (self.squares[(i, c)][1].notation != "Kb"):
                        pin2.append(self.squares[(i, c)][1].notation)
                        add_legal_moves.append((i,c))

                        pinned_a_piece = False
                        for j in range(i+1,8):
                            if j > 7:
                                j=8
                                break
                            elif (self.squares[(j, c)][1] != None):
                                if (self.squares[(j, c)][1].color != actual_piece.color) and (self.squares[(j, c)][1].notation == "K" or self.squares[(j, c)][1].notation == "Kb"):
                                    pin2.append(self.squares[(j, c)][1].notation)
                                    if len(pin2) >= 2 and (pin2[1] == "K" or pin2[1] == "Kb"):
                                        pinned_a_piece = True
                                    j=8
                                    break
                                else:
                                    j=8
                                    break
                            else:
                                add_pin_pathway.append((j, c))
                        if pinned_a_piece:
                            self.squares[(i, c)][1].pinned = True
                            add_pin_pathway.extend(add_check_pathway)
                            actual_piece.pin_pathway.extend(add_pin_pathway)
                        else:
                            self.squares[(i, c)][1].pinned = False

                        i=-1
                        break
                    else:
                        add_legal_moves.append((i,c))
                        self.squares[(i, c)][1].in_check = True 
                        # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")
                        actual_piece.check_pathway = [pos for pos in add_check_pathway]
                        i=-1
                        break
                # a piece below that is an ally has been reached
                elif (self.squares[(i, c)][1] != None) and (self.squares[(i, c)][1].color == actual_piece.color):
                    add_defends.append((i,c))
                    if self.squares[(i, c)][1].notation == "K" or self.squares[(i, c)][1].notation == "Kb":
                        add_defends.remove((i,c))
                    i=-1
                    break
            add_check_pathway = []

            actual_piece.defends = add_defends
            return add_legal_moves
        #endregion

        #region black PAWN get legal moves
        if actual_piece.notation == "Pb":
            add_legal_moves = []
            add_defends = []

            for key, val in self.squares.items():
                if (val[1] != None): # there is a piece at the current square
                    # diagonal left has an enemy
                    if (val[1].pos_r == r+1) and (val[1].pos_c == c-1) and ((val[1].color != actual_piece.color)) and (val[1].pos_r>=0 and val[1].pos_r<=7) and (val[1].pos_c>=0 and val[1].pos_c<=7) and (val[1].notation != "K" and val[1].notation != "Kb"):
                        add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                    elif (val[1].pos_r == r+1) and (val[1].pos_c == c-1) and ((val[1].color != actual_piece.color)) and (val[1].pos_r>=0 and val[1].pos_r<=7) and (val[1].pos_c>=0 and val[1].pos_c<=7) and (val[1].notation == "K" or val[1].notation == "Kb"):
                        add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                        val[1].in_check = True 
                        # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")
                    # diagonal right has an enemy
                    if (val[1].pos_r == r+1) and (val[1].pos_c == c+1) and ((val[1].color != actual_piece.color)) and (val[1].pos_r>=0 and val[1].pos_r<=7) and (val[1].pos_c>=0 and val[1].pos_c<=7) and (val[1].notation != "K" and val[1].notation != "Kb"):
                        add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                    elif (val[1].pos_r == r+1) and (val[1].pos_c == c+1) and ((val[1].color != actual_piece.color)) and (val[1].pos_r>=0 and val[1].pos_r<=7) and (val[1].pos_c>=0 and val[1].pos_c<=7) and (val[1].notation == "K" or val[1].notation == "Kb"):
                        add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                        val[1].in_check = True 
                        # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")

                    # diagonal left has an ally
                    if (val[1].pos_r == r+1) and (val[1].pos_c == c-1) and ((val[1].color == actual_piece.color)) and (val[1].pos_r>=0 and val[1].pos_r<=7) and (val[1].pos_c>=0 and val[1].pos_c<=7) and (val[1].notation != "K" and val[1].notation != "Kb"):
                        add_defends.append((val[1].pos_r, val[1].pos_c))
                    # diagonal right has an ally
                    if (val[1].pos_r == r+1) and (val[1].pos_c == c+1) and ((val[1].color == actual_piece.color)) and (val[1].pos_r>=0 and val[1].pos_r<=7) and (val[1].pos_c>=0 and val[1].pos_c<=7) and (val[1].notation != "K" and val[1].notation != "Kb"):
                        add_defends.append((val[1].pos_r, val[1].pos_c))
                    
                    # on left there's an enemy pawn that GAVE ME en passant
                    if (val[1].pos_r == r) and (val[1].pos_c == c-1) and (val[1].notation == "P"):
                        if val[1].get_en_pass == True:
                            if (actual_piece.do_en_pass == True):
                                add_legal_moves.append((val[1].pos_r+1, val[1].pos_c))
                            print("LEFT ENEMY GAVE EN PASS -> WHITE")
                    # on right there's an enemy pawn that GAVE ME en passant
                    if (val[1].pos_r == r) and (val[1].pos_c == c+1) and (val[1].notation == "P"):
                        if val[1].get_en_pass == True:
                            if (actual_piece.do_en_pass == True):
                                add_legal_moves.append((val[1].pos_r+1, val[1].pos_c))
                                print("RIGHT ENEMY GAVE EN PASS -> WHITE")
                else:
                    # diagonal left has no piece
                    if (key[0] == r+1) and (key[1] == c-1) and (key[0]>=0 and key[0]<=7) and (key[1]>=0 and key[1]<=7):
                        add_defends.append((key[0], key[1]))
                    # diagonal left has no piece
                    if (key[0] == r+1) and (key[1] == c+1) and (key[0]>=0 and key[0]<=7) and (key[1]>=0 and key[1]<=7):
                        add_defends.append((key[0], key[1]))
                    
                    # no piece one space ahead
                    if (key == (r+1, c)): 
                        add_legal_moves.append((r+1, c))
                    # no piece in path of two space jump and can still do two spaces
                    if (key == (r+1, c)) and (actual_piece.two_spaces == True) and (self.squares[(r+2, c)][1] == None): 
                        add_legal_moves.append((r+2, c))

            actual_piece.defends = add_defends   
            return add_legal_moves
        #endregion

        #region white PAWN get legal moves
        if actual_piece.notation == "P":
            add_legal_moves = []
            add_defends = []

            for key, val in self.squares.items():
                if (val[1] != None): # there is a piece at the current square
                    # diagonal left has an enemy
                    if (val[1].pos_r == r-1) and (val[1].pos_c == c-1) and ((val[1].color != actual_piece.color)) and (val[1].pos_r>=0 and val[1].pos_r<=7) and (val[1].pos_c>=0 and val[1].pos_c<=7) and (val[1].notation != "K" and val[1].notation != "Kb"):
                        add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                    elif (val[1].pos_r == r-1) and (val[1].pos_c == c-1) and ((val[1].color != actual_piece.color)) and (val[1].pos_r>=0 and val[1].pos_r<=7) and (val[1].pos_c>=0 and val[1].pos_c<=7) and (val[1].notation == "K" or val[1].notation == "Kb"):
                        add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                        val[1].in_check = True 
                        # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")
                    # diagonal right has an enemy
                    if (val[1].pos_r == r-1) and (val[1].pos_c == c+1) and ((val[1].color != actual_piece.color)) and (val[1].pos_r>=0 and val[1].pos_r<=7) and (val[1].pos_c>=0 and val[1].pos_c<=7) and (val[1].notation != "K" and val[1].notation != "Kb"):
                        add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                    elif (val[1].pos_r == r-1) and (val[1].pos_c == c+1) and ((val[1].color != actual_piece.color)) and (val[1].pos_r>=0 and val[1].pos_r<=7) and (val[1].pos_c>=0 and val[1].pos_c<=7) and (val[1].notation == "K" or val[1].notation == "Kb"):
                        add_legal_moves.append((val[1].pos_r, val[1].pos_c))
                        val[1].in_check = True 
                        # print(f"{actual_piece.notation} at ({actual_piece.pos_r},{actual_piece.pos_c}) has CHANGED IT")

                    # diagonal left has an ally
                    if (val[1].pos_r == r-1) and (val[1].pos_c == c-1) and ((val[1].color == actual_piece.color)) and (val[1].pos_r>=0 and val[1].pos_r<=7) and (val[1].pos_c>=0 and val[1].pos_c<=7) and (val[1].notation != "K" and val[1].notation != "Kb"):
                        add_defends.append((val[1].pos_r, val[1].pos_c))
                    # diagonal right has an ally
                    if (val[1].pos_r == r-1) and (val[1].pos_c == c+1) and ((val[1].color == actual_piece.color)) and (val[1].pos_r>=0 and val[1].pos_r<=7) and (val[1].pos_c>=0 and val[1].pos_c<=7) and (val[1].notation != "K" and val[1].notation != "Kb"):
                        add_defends.append((val[1].pos_r, val[1].pos_c))

                    # on left there's an enemy pawn that GAVE ME en passant
                    if (val[1].pos_r == r) and (val[1].pos_c == c-1) and (val[1].notation == "Pb"):
                        if val[1].get_en_pass == True:
                            if (actual_piece.do_en_pass == True):
                                add_legal_moves.append((val[1].pos_r-1, val[1].pos_c))
                            # print("LEFT ENEMY GAVE EN PASS -> BLACK")
                    # on right there's an enemy pawn that GAVE ME en passant
                    if (val[1].pos_r == r) and (val[1].pos_c == c+1) and (val[1].notation == "Pb"):
                        if val[1].get_en_pass == True: 
                            if (actual_piece.do_en_pass == True):
                                add_legal_moves.append((val[1].pos_r-1, val[1].pos_c))
                            # print("RIGHT ENEMY GAVE EN PASS -> BLACK")
                else:
                    # diagonal left has no piece
                    if (key[0] == r-1) and (key[1] == c-1) and (key[0]>=0 and key[0]<=7) and (key[1]>=0 and key[1]<=7):
                        add_defends.append((key[0], key[1]))
                    # diagonal right has no piece
                    if (key[0] == r-1) and (key[1] == c+1) and (key[0]>=0 and key[0]<=7) and (key[1]>=0 and key[1]<=7):
                        add_defends.append((key[0], key[1]))

                    # no piece one space ahead
                    if (key == (r-1, c)): 
                        add_legal_moves.append((r-1, c))
                    # no piece two spaces ahead and can still do that
                    if (key == (r-1, c)) and (actual_piece.two_spaces == True) and (self.squares[(r-2, c)][1] == None):  
                        add_legal_moves.append((r-2, c))
                    
            actual_piece.defends = add_defends
            return add_legal_moves
        #endregion

#region start game
root = tk.Tk()
root.title("Chess Game")
root.configure(bg="#242320")
board = ChessBoard(root, size=800)
board.pack()
board.create_board()
board.place_piece("Pb", "black", 1, 0, [(2,0), (3,0)], [], two_spaces=True, do_en_pass=False, get_en_pass=False, en_pass_count=0, pinned=False)
board.place_piece("Pb", "black", 1, 1, [(2,1), (3,1)], [], two_spaces=True, do_en_pass=False, get_en_pass=False, en_pass_count=0, pinned=False)
board.place_piece("Pb", "black", 1, 2, [(2,2), (3,2)], [], two_spaces=True, do_en_pass=False, get_en_pass=False, en_pass_count=0, pinned=False)
board.place_piece("Pb", "black", 1, 3, [(2,3), (3,3)], [], two_spaces=True, do_en_pass=False, get_en_pass=False, en_pass_count=0, pinned=False)
board.place_piece("Pb", "black", 1, 4, [(2,4), (3,4)], [], two_spaces=True, do_en_pass=False, get_en_pass=False, en_pass_count=0, pinned=False)
board.place_piece("Pb", "black", 1, 5, [(2,5), (3,5)], [], two_spaces=True, do_en_pass=False, get_en_pass=False, en_pass_count=0, pinned=False)
board.place_piece("Pb", "black", 1, 6, [(2,6), (3,6)], [], two_spaces=True, do_en_pass=False, get_en_pass=False, en_pass_count=0, pinned=False)
board.place_piece("Pb", "black", 1, 7, [(2,7), (3,7)], [], two_spaces=True, do_en_pass=False, get_en_pass=False, en_pass_count=0, pinned=False)
board.place_piece("Rb", "black", 0, 0, [], [(1,0), (0,1)], moved=False, check_pathway=[], pinned=False, pin_pathway=[])
board.place_piece("Rb", "black", 0, 7, [], [(1,7), (0,6)], moved=False, check_pathway=[], pinned=False, pin_pathway=[])
board.place_piece("Nb", "black", 0, 1, [(2,0), (2,2)], [(1,3)], pinned=False)
board.place_piece("Nb", "black", 0, 6, [(2,7), (2,5)], [(1,4)], pinned=False)
board.place_piece("Bb", "black", 0, 2, [], [(1,1), (1,3)], check_pathway=[], pinned=False, pin_pathway=[])
board.place_piece("Bb", "black", 0, 5, [], [(1,4), (1,6)], check_pathway=[], pinned=False, pin_pathway=[])
board.place_piece("Qb", "black", 0, 3, [], [(0,2), (1,2), (1,3), (1,4), (0,4)], check_pathway=[], pinned=False, pin_pathway=[])
board.place_piece("Kb", "black", 0, 4, [], [(0,3), (1,3), (1,4), (1,5), (0,5)], moved=False, border=[(0,3), (1,3), (1,4), (1,5), (0,5)], in_check=False)

board.place_piece("P", "white", 6, 0, [(5, 0), (4, 0)], [], two_spaces=True, do_en_pass=False, get_en_pass=False, en_pass_count=0, pinned=False)
board.place_piece("P", "white", 6, 1, [(5, 1), (4, 1)], [], two_spaces=True, do_en_pass=False, get_en_pass=False, en_pass_count=0, pinned=False)
board.place_piece("P", "white", 6, 2, [(5, 2), (4, 2)], [], two_spaces=True, do_en_pass=False, get_en_pass=False, en_pass_count=0, pinned=False)
board.place_piece("P", "white", 6, 3, [(5, 3), (4, 3)], [], two_spaces=True, do_en_pass=False, get_en_pass=False, en_pass_count=0, pinned=False)
board.place_piece("P", "white", 6, 4, [(5, 4), (4, 4)], [], two_spaces=True, do_en_pass=False, get_en_pass=False, en_pass_count=0, pinned=False)
board.place_piece("P", "white", 6, 5, [(5, 5), (4, 5)], [], two_spaces=True, do_en_pass=False, get_en_pass=False, en_pass_count=0, pinned=False)
board.place_piece("P", "white", 6, 6, [(5, 6), (4, 6)], [], two_spaces=True, do_en_pass=False, get_en_pass=False, en_pass_count=0, pinned=False)
board.place_piece("P", "white", 6, 7, [(5, 7), (4, 7)], [], two_spaces=True, do_en_pass=False, get_en_pass=False, en_pass_count=0, pinned=False)
board.place_piece("R", "white", 7, 0, [], [(6,0), (7,1)], moved=False, check_pathway=[], pinned=False, pin_pathway=[])
board.place_piece("R", "white", 7, 7, [], [(6,7), (7,6)], moved=False, check_pathway=[], pinned=False, pin_pathway=[])
board.place_piece("N", "white", 7, 1, [(5,0),(5,2)], [(6, 3)], pinned=False)
board.place_piece("N", "white", 7, 6, [(5,7), (5,5)], [(6, 4)], pinned=False)
board.place_piece("B", "white", 7, 2, [], [(6,1), (6,3)], check_pathway=[], pinned=False, pin_pathway=[])
board.place_piece("B", "white", 7, 5, [], [(6,4), (6,6)], check_pathway=[], pinned=False, pin_pathway=[])
board.place_piece("Q", "white", 7, 3, [], [(7,2), (6,2), (6,3), (6,4), (7,4)], check_pathway=[], pinned=False, pin_pathway=[])
board.place_piece("K", "white", 7, 4, [], [(7,3), (6,3), (6,4), (6,5), (7,5)], moved=False, border=[(7,3), (6,3), (6,4), (6,5), (7,5)], in_check=False)
# print(board.squares[(0, 1)][1])
board.game_states.append(copy.deepcopy(board.squares))

def show_rules():
    rules_text = (
        "Chess Game Rules:\n"
        "1. Click-to-move\n"
        "2. There is no draw button so verbal draws will be used instead\n"
    )
    # Display a messagebox with the custom rules
    messagebox.showinfo("Custom Chess Rules", rules_text)
delay_time = 500
root.after(delay_time, show_rules)

root.mainloop()
#endregion