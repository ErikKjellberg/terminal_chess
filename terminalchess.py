import os
import sys
import time
import random
import chess
import chess.engine
import copy
from stockfish import Stockfish
import chessparser as parser
import choices
import inspect
import json

fg_black = "\u001b[30m"
fg_white = "\u001b[37m"
fg_bw = [fg_black, fg_white]
bg_black = "\u001b[40m"
bg_white = "\u001b[47m"
bg_bw = [bg_black, bg_white]
reset = "\u001b[0m"

class Settings:
    def __init__(self):
        self.settings = self.get_settings()
        print(self.settings)

    def get_settings(self):
        #os.system("clear")
        with open("settings.txt") as f:
            data = json.load(f)
        return data


class Piece:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.pos = [self.x, self.y]
        self.color = color
        self.moved = False

    def attempt_move(self, square):
        move = [square[0]-self.x, square[1]-self.y]
        #print("Attempting move: ",move)
        if move in self.allowed_moves:
            #print("LEGAL MOVE!")
            return True
        #print("ILLEGAL MOVE!")
        return False

    def move(self, square):
        self.x = square[0]
        self.y = square[1]
        self.pos = [self.x, self.y]
        self.moved = True


class King(Piece):
    def __init__(self, x, y, color):
        self.allowed_moves = [[-1,-1],[0,-1],[1,-1],[-1,0],[1,0],[-1,1],[0,1],[1,1]]
        self.symbols = [chr(9818), chr(9812)]
        self.letter = "K"
        self.value = 999
        super(King, self).__init__(x, y, color)


class Queen(Piece):
    def __init__(self, x, y, color):
        self.allowed_moves = []
        self.symbols = [chr(9819), chr(9813)]
        self.letter = "Q"
        self.value = 9
        super(Queen, self).__init__(x, y, color)


class Rook(Piece):
    def __init__(self, x, y, color):
        self.allowed_moves = []
        self.symbols = [chr(9820), chr(9814)]
        self.letter = "R"
        self.value = 5
        super(Rook, self).__init__(x, y, color)


class Bishop(Piece):
    def __init__(self, x, y, color):
        self.allowed_moves = []
        self.symbols = [chr(9821), chr(9815)]
        self.letter = "B"
        self.value = 3
        super(Bishop, self).__init__(x, y, color)


class Knight(Piece):
    def __init__(self, x, y, color):
        self.allowed_moves = [[-1, 2],[1,2],[-1,-2],[1,-2],[2,-1],[2,1],[-2,-1],[-2,1]]
        self.symbols = [chr(9822), chr(9816)]
        self.letter = "N"
        self.value = 3
        super(Knight, self).__init__(x, y, color)


class Pawn(Piece):
    def __init__(self, x, y, color):
        self.allowed_moves = [[-1,-1],[0,-1],[1,-1],[-1,0],[1,0],[-1,1],[0,1],[1,1]]
        self.symbols = [chr(9823), chr(9817)]
        self.letter = "P"
        self.value = 1
        self.en_passantable = False
        super(Pawn, self).__init__(x, y, color)


class Board:
    def __init__(self, pos_string=None):
        """self.square_list = [[None for i in range(8)] for j in range(8)]
        self.square_list[0] = [Rook(0, 0, 1), Knight(1, 0, 1), Bishop(2, 0, 1), Queen(3, 0, 1), King(4, 0, 1), Bishop(5, 0, 1), Knight(6, 0, 1), Rook(7, 0, 1)]
        self.square_list[1] = [Pawn(i, 1, 1) for i in range(8)]
        self.square_list[6] = [Pawn(i, 6, 0) for i in range(8)]
        self.square_list[7] = [Rook(0, 7, 0), Knight(1, 7, 0), Bishop(2, 7, 0), Queen(3, 7, 0), King(4, 7, 0), Bishop(5, 7, 0), Knight(6, 7, 0), Rook(7, 7, 0)]"""
        self.width = 8
        self.flipped = False
        self.piece_list = []
        self.taken_pieces = [[],[]]
        self.piece_types = {"K": King, "Q": Queen, "R": Rook, "B": Bishop, "N": Knight, "P": Pawn}
        if pos_string == None:
            #self.piece_list = [King(5, 5, 1), King(7, 5, 0), Rook(5, 7, 0), Pawn(4, 5, 1), Pawn(6, 5, 1), Pawn(4, 4, 1), Pawn(5, 4, 1), Pawn(6, 4, 1)]

            # regular game setup
            self.piece_list = [Rook(0, 0, 1), Knight(1, 0, 1), Bishop(2, 0, 1), Queen(3, 0, 1), King(4, 0, 1), Bishop(5, 0, 1), Knight(6, 0, 1), Rook(7, 0, 1), \
            Rook(0, 7, 0), Knight(1, 7, 0), Bishop(2, 7, 0), King(4, 7, 0), Bishop(5, 7, 0), Knight(6, 7, 0), Rook(7, 7, 0)]
            for i in range(self.width):
                self.piece_list.append(Pawn(i, 1, 1))
                self.piece_list.append(Pawn(i, 6, 0))
        else:
            piece_strings = pos_string.split("__")[0].split("_")
            for piece_string in piece_strings:
                piece_to_add = self.piece_types[piece_string[0]](int(piece_string[1]), int(piece_string[2]), int(piece_string[3]))
                if type(piece_to_add) == Pawn:
                    self.en_passantable = [False, True][int(piece_string[4])]
                self.piece_list.append(piece_to_add)
            taken_strings = pos_string.split("__")[1].split("_")
            if taken_strings != ["0"]:
                for taken_string in taken_strings:
                    piece_to_add = self.piece_types[taken_string[0]](int(taken_string[1]), int(taken_string[2]), int(taken_string[3]))
                    self.taken_pieces[(piece_to_add.color + 1) % 2].append(piece_to_add)

        self.material_imbalance = sum([p.value * [-1, 1][p.color] for p in self.piece_list])

    def draw(self):
        for i in range(len(self.taken_pieces)):
            self.taken_pieces[i].sort(key=lambda p: {"P": 0, "N": 1, "B": 2, "R": 3, "Q": 4, "K": 5}[p.letter])
        print(fg_bw[1]+"".join([p.symbols[(p.color + 1) % 2] for p in self.taken_pieces[self.flipped]]), end="")
        if self.material_imbalance*[1, -1][self.flipped] < 0:
            print(" +"+str(abs(self.material_imbalance)), end="")
        print(reset)
        for i in range(self.width) if self.flipped else reversed(range(self.width)):
            c = i % 2
            print(str(i+1) + " ", end="")
            for j in range(self.width) if not self.flipped else reversed(range(self.width)):
                print(bg_bw[(c+j)%2], end="")
                is_piece = False
                for piece in self.piece_list:
                    if j == piece.x and i == piece.y:
                        is_piece = True
                        print((fg_bw[(piece.color+1)%2] + piece.symbols[1]), end="") if piece.color == (c+j)%2 else print((fg_bw[(piece.color)%2] + piece.symbols[0]), end="")
                        #print((fg_bw[(piece.color+1)%2] + [piece.letter.lower(), piece.letter.upper()][piece.color]), end="") if piece.color == (c+j)%2 \
                        #else print((fg_bw[(piece.color)%2] + [piece.letter.lower(), piece.letter.upper()][piece.color]), end="")
                        print(" ", end="")
                        break
                if not is_piece:
                    print("  ", end="")
            print(reset)
        print(["  a b c d e f g h", "  h g f e d c b a"][1 if self.flipped else 0])
        print(fg_bw[1]+"".join([p.symbols[(p.color + 1) % 2] for p in self.taken_pieces[(self.flipped + 1) % 2]]), end="")
        if self.material_imbalance*[1, -1][self.flipped] > 0:
            print(" +"+str(abs(self.material_imbalance)), end="")
        print(reset)
        # shit
        """print(str(i+1) + " " + " ".join([bg_bw[(c+j)%2] + \
        (((fg_bw[(piece.color+1)%2] + piece.symbols[1]) if piece.color == (c+j)%2 else (fg_bw[(piece.color)%2] + piece.symbols[0])) \
        if (i == piece.x and j == piece.y for piece in self.piece_list) \
        else " ") \
        for j in range(8)])+ " " + reset)"""

    """for i, row in reversed(list(enumerate(self.square_list))):
        c = i % 2
        print(str(i+1) + " " + " ".join([bg_bw[(c+j)%2] + \
        (((fg_bw[(square.color+1)%2] + square.symbols[1]) if square.color == (c+j)%2 else (fg_bw[(square.color)%2] + square.symbols[0])) if square != None else " ") \
        for j, square in enumerate(row)])+ " " + reset)
        """"""(((fg_bw[(square.color+1)%2] + square.symbols[0]) if square.color == (c+j)%2 else (fg_bw[(square.color)%2] + square.symbols[1])) if square != None else " ") \
        for j, square in enumerate(row)])+ " " + reset)"""

    def flip(self):
        self.flipped = not self.flipped

class GameManager:
    def __init__(self, board, player_types, pos_string = None):
        self.board = board
        self.pieces = {"K": King, "Q": Queen, "R": Rook, "B": Bishop, "N": Knight, "P": Pawn}
        self.players = ["Black", "White"]
        self.pc_pl = ["STOCKFISH", "PLAYER"]
        self.player_types = player_types
        self.cpus = []
        for i in self.player_types:
            if i == 0:
                self.cpus.append(create_fish())
        if self.player_types != [1, 1]:
            self.fish = create_fish()
            self.fish.depth = 10
        self.current_turn = 1
        self.full_moves = 1
        self.moves_since_lpm = 0
        self.moves_since_lc = 0
        if pos_string != None:
            strings = pos_string.split("__")[2].split("_")
            for piece in self.board.piece_list:
                if type(piece) == Rook:
                    piece.moved = True
            castlings = [[],[]]
            castlings[0] = [strings[0][0], strings[0][1]]
            castlings[1] = [strings[0][2], strings[0][3]]
            for i in range(len(castlings)):
                for j in range(len(castlings[i])):
                    if castlings[i][j] == 1:
                        for piece in self.board.piece_list:
                            if type(self.piece) == Rook and self.color == i and self.x == [0, 7][j] and self.y == [7, 0][i]:
                                piece.moved = False
            self.moves_since_lc = int(strings[1])
            self.moves_since_lpm = int(strings[2])
            self.current_turn = int(strings[3])
            self.full_moves = int(strings[4])
        self.game = [self.to_string(self.board.piece_list)]
        self.running = True

    def attempt_move(self, piece, square, checkforcheck, promotion_piece, conditions=None):
        fail = False
        global take, long_castle, short_castle, promotion
        take, long_castle, short_castle, promotion = False, False, False, False
        if conditions != None:
            for i, n in enumerate(conditions):
                temp = conditions[i]
                globals()[temp] = True

        """if checkforcheck:
            original_board = [r for r in self.board.piece_list]
            #print(len(original_board))
            #self.board.draw()
            ppos = piece.pos
            thedeadone = None
            for p in self.board.piece_list:
                if p.pos == square:
                    thedeadone = p
            self.take(square)
            piece.move(square)
            if self.check(piece.color, promotion=promotion_piece):
                print("It is check!!")
                input()
                fail = True
            #print(len(self.board.piece_list))
            piece.move(ppos)
            if thedeadone != None:
                self.board.piece_list.append(thedeadone)
            if fail:
                return False"""
        for p in self.board.piece_list:
            if p.pos == square and not take:
                return False
            if p.pos == square and take and p.color == piece.color:
                return False
        if piece != None and [piece.x, piece.y] == square:
            return False

        if long_castle or short_castle:
            if short_castle:
                n = 0
            else:
                n = 1
            #print("HAHAHA1")
            #time.sleep(0.5)
            if self.castle(n, self.current_turn):
                return True
            else:
                return False
        if type(piece) == Bishop or type(piece) == Queen:
            # print("WE are here, it's a bishop or a queen.")
            # DO LATER, problems here that need to be solved, yes indeed
            if square[0]-piece.x != 0 and square[1]-piece.y:
                dx = abs(square[0]-piece.x)/(square[0]-piece.x)
                dy = abs(square[1]-piece.y)/(square[1]-piece.y)
            else:
                fail = True
                if type(piece) == Bishop: return False
            if abs(piece.x - square[0]) != abs(piece.y - square[1]):
                """print("Not a diagonal")
                print("X diff" + str(piece.x - square[0]))
                print("Y diff" + str(piece.y - square[1]))"""
                fail = True
                if type(piece) == Bishop: return False
            if not fail:
                for i in range(1, abs(square[0]-piece.x)):
                    for p in self.board.piece_list:
                        #print(p.pos)
                        if [piece.x + dx*i, piece.y + dy*i] == p.pos and i != 0:
                            # print("A piece is in the way")
                            fail = True
                            if type(piece) == Bishop: return False
            if not fail: return True

        if type(piece) == Rook or type(piece) == Queen:
            if piece.x == square[0]:
                d = abs(square[1]-piece.y)/(square[1]-piece.y)
                for i in range(0, abs(square[1]-piece.y)):
                    for p in self.board.piece_list:
                        if [piece.x, piece.y + d*i] == p.pos and i != 0:
                            # print("A piece is in the way")
                            return False
            elif piece.y == square[1]:
                d = abs(square[0]-piece.x)/(square[0]-piece.x)
                for i in range(0, abs(square[0]-piece.x)):
                    for p in self.board.piece_list:
                        if [piece.x + d*i, piece.y] == p.pos and i != 0:
                            # print("A piece is in the way")
                            return False
            else:
                return False
            return True

        elif type(piece) == Pawn:
            fail = True
            # taking
            if take and (square[0] - piece.x == 1 or square[0] - piece.x == -1) and square[1] - piece.y == [-1, 1][piece.color]:
                for p in self.board.piece_list:
                    #taking regularly
                    if [p.x, p.y] == square:
                        fail = False
                    #taking en passant
                    elif type(p) == Pawn and p.en_passantable and [p.x, p.y+[-1,1][self.current_turn]] == square:
                        return "en passant"
            # walking forward one step
            elif square[0] - piece.x == 0 and square[1] - piece.y == [-1, 1][piece.color]:
                for p in self.board.piece_list:
                    if [piece.x, piece.y + [-1, 1][piece.color]] == p.pos and p != piece:
                        return False
                fail = False
            # walking forward two steps
            elif square[0] - piece.x == 0 and square[1] - piece.y == [-2, 2][piece.color] and piece.y == [6, 1][piece.color]:
                for p in self.board.piece_list:
                    if [piece.x, piece.y + [-1, 1][piece.color]] == p.pos or [piece.x, piece.y + [-2, 2][piece.color]] == p.pos and p != piece:
                        return False
                fail = False
                piece.en_passantable = True
            if not fail:
                if promotion and square[1] == [0, 7][piece.color]:
                    return promotion_piece
                if not promotion and square[1] != [0, 7][piece.color]:
                    return True
                else:
                    return False
                    piece.en_passantable = False
            else:
                return False
        elif not piece.attempt_move(square):
            return False
        else:
            return True

    def castle(self, length, color):
        king_square_list = [[[6,7],[2,7]],[[6,0],[2,0]]]
        rook_square_list = [[[5,7],[3,7]],[[5,0],[3,0]]]
        king_square = king_square_list[color][length]
        rook_square = rook_square_list[color][length]
        #print(king_square[0]+1)
        for x in range(4, king_square[0] + [1,-1][length], [1,-1][length]):
            if self.check(self.current_turn, square = [x, king_square[1]]):
                return False
            if x!=4:
                for p in self.board.piece_list:
                    if p.x == x and p.y == king_square[1]:
                        return False
        b1 = False
        b2 = False
        for p in self.board.piece_list:
            if type(p) == King and p.color == color and not p.moved:
                the_king = p
                b1 = True
            if type(p) == Rook and p.pos == [[7, rook_square[1]],[0, rook_square[1]]][length] and p.color == color and not p.moved:
                the_rook = p
                b2 = True
        if b1 and b2:
            the_king.move(king_square)
            the_rook.move(rook_square)
            return True
        else:
            return False

    def take(self, square):
        for p in self.board.piece_list:
            if [p.x, p.y] == square:
                self.board.taken_pieces[(p.color + 1) % 2].append(p)
                self.board.piece_list.remove(p)

    def check(self, color, promotion=None, square=None):
        for p in self.board.piece_list:
            if type(p) == King and p.color == color:
                # print("we are here")
                king = p
                pos = king.pos
        if square != None:
            pos = square
        for p in self.board.piece_list:
            if p.color == (color + 1) % 2:
                if type(p) == King and abs(p.x - pos[0]) < 2 and abs(p.y - pos[1]) < 2:
                    return True
                if self.attempt_move(p, pos, True, None, conditions=["take"]):
                    return True
                if type(p) == Pawn:
                    for P in ["Q", "R", "B", "N"]:
                        if self.attempt_move(p, pos, False, P, conditions=["take", "promotion"]):
                            return True
        # print("No check.")
        return False

    def promote(self, piece_1, piece_2, square):
        """done = False
        for p in self.board.piece_list:
            if p.x == square[0] and p.y == square[1]:
                color = p.color
                self.board.piece_list.remove(p)
                done = True
                break
        if done:
            self.board.piece_list.append(self.pieces[piece](square[0], square[1], color))"""
        self.board.piece_list.append(self.pieces[piece_2](square[0], square[1], piece_1.color))
        for piece in self.board.taken_pieces[(piece_1.color + 1) % 2]:
            if piece.letter == piece_2:
                self.board.taken_pieces[(piece_1.color + 1) % 2].remove(piece)
                break
        self.board.taken_pieces[(piece_1.color + 1) % 2].append(piece_1)
        self.board.piece_list.remove(piece_1)

    def checkcheckmatestalemate(self, color):
        board_copy_1 = copy.deepcopy(self.board.piece_list)
        #self.board.piece_list.sort(key=lambda p: {"P": 0, "N": 1, "B": 2, "R": 3, "Q": 4, "K": 5}[p.letter])
        for piece in self.board.piece_list:
            #print([p.letter+str(p.x)+str(p.y)+str(p.color) for p in self.board.piece_list])
            #print("BUHU",piece.letter,str(piece.x),str(piece.y), str(piece.color))
            if piece.color == color:
                #print("HEHE")
                for x in range(self.board.width):
                    for y in range(self.board.width):
                        if self.attempt_move(piece, [x,y], True, None) or self.attempt_move(piece, [x,y], True, None, conditions=["take"]) or\
                        self.attempt_move(piece, [x,y], True, "Q", conditions = ["promotion"]) or self.attempt_move(piece, [x,y], True, "Q", conditions = ["take", "promotion"]):
                            # print("We got here right, and the move was: ",piece.letter+str(["a", "b", "c", "d", "e", "f", "g", "h"][x])+str(y+1))
                            a, b = piece.x, piece.y
                            piece_to_take = None
                            for i, p in enumerate(self.board.piece_list):
                                if p.x == x and p.y == y and p != piece:
                                    piece_to_take = p
                                    #print("Taking",piece_to_take.letter,str(piece_to_take.x),str(piece_to_take.y), str(piece_to_take.color))
                                    break
                            if piece_to_take != None:
                                self.take([x,y])
                            piece.move([x,y])
                            #print("It moved",piece.letter,str(piece.x),str(piece.y), str(piece.color))
                            #print([p.letter+str(p.x)+str(p.y)+str(p.color) for p in self.board.piece_list])
                            #print(self.check(color))
                            if not self.check(color):
                                #print("WE ARE VEVENQOJIN")
                                piece.move([a,b])
                                piece.moved = False
                                if piece_to_take != None:
                                    self.board.piece_list.insert(i, piece_to_take)
                                    self.board.taken_pieces[color].remove(piece_to_take)
                                return False
                            else:
                                piece.move([a,b])
                                piece.moved = False
                                if piece_to_take != None:
                                    self.board.piece_list.insert(i, piece_to_take)
                                    self.board.taken_pieces[color].remove(piece_to_take)
                        #self.board.piece_list.sort(key=lambda p: {"P": 0, "N": 1, "B": 2, "R": 3, "Q": 4, "K": 5}[p.letter])
        return True

    def checkinsufficientmaterial(self):
        piece_types = "".join(sorted([piece.letter for piece in self.board.piece_list]))
        insuff_material_list = ["KK", "KKN", "BKK"]
        if piece_types in insuff_material_list:
            return True
        if piece_types == "BBKK":
            bishops = [piece for piece in self.board.piece_list if type(piece) == Bishop]
            if (abs(bishops[0].x - bishops[1].x) + abs(bishops[0].y - bishops[1].y)) % 2 == 0 and bishops[0].color != bishops[1].color:
                return True
        return False

    def checkdrawbyrep(self):
        if len(self.game) >= 5:
            #for j in self.game:
                #print(", ".join([i.letter+str(i.x)+str(i.y) for i in j]))
            count = 1
            for position in self.game[:-1]:
                if position[:-10] == self.game[-1][:-10]:
                    count += 1
            if count == 3:
                return True
        else:
            return False

    def checkdrawby50moverule(self):
        if self.moves_since_lc >= 100 and self.moves_since_lpm >= 100:
            return True
        else:
            return False

    def endgame(self, message):
        print(message)
        input()
        self.running = False

    def to_string(self, position):
        pos_string = ""
        for piece in position:
            pos_string += piece.letter+str(piece.x)+str(piece.y)+str(piece.color)
            if piece.letter == "P":
                if piece.en_passantable:
                    pos_string += "1"
                else:
                    pos_string += "0"
            pos_string += "_"
        pos_string += "_"
        if len(self.board.taken_pieces[0])+len(self.board.taken_pieces[1]) == 0:
            pos_string += "0_"
        for piece_sides in self.board.taken_pieces:
            for piece in piece_sides:
                pos_string += piece.letter+str(piece.x)+str(piece.y)+str(piece.color)+"_"
        pos_string += "_"
        temp = copy.deepcopy(self.board.piece_list)
        castlings = [["0", "0"], ["0", "0"]]
        rooks = [p for p in self.board.piece_list if type(p) == Rook]
        for p in rooks:
            if not p.moved and p.x == 0 and p.y == [7, 0][p.color]:
                castlings[p.color][0] = "1"
            if not p.moved and p.x == 7 and p.y == [7, 0][p.color]:
                castlings[p.color][1] = "1"
        kings = [p for p in self.board.piece_list if type(p) == King]
        for p in kings:
            if p.moved:
                castlings[p.color] = ["0", "0"]
        """for i in range(2):
            for j in range(2):
                if self.castle(i, j):
                    pos_string += "1"
                else:
                    pos_string += "0"
                self.board.piece_list = temp
                temp = copy.deepcopy(self.board.piece_list)"""
        pos_string += "".join(i for c in castlings for i in c)
        pos_string += "_"+str(self.moves_since_lc)
        pos_string += "_"+str(self.moves_since_lpm)
        pos_string += "_"+str(self.current_turn)
        pos_string += "_"+str(self.full_moves)
        return pos_string

    def to_FEN(self, position):
        FEN = ""
        board = [[0 for i in range(8)] for i in range(8)]
        for piece in position:
            board[piece.y][piece.x] = piece
        for i, row in enumerate(reversed(board)):
            n = 0
            for square in row:
                if square == 0:
                    n += 1
                else:
                    if n != 0:
                        FEN+=str(n)
                    if square.color == 0:
                        FEN+=square.letter.lower()
                    else:
                        FEN+=square.letter.upper()
                    n = 0
            if n != 0:
                FEN += str(n)
            if i < 7:
                FEN += "/"
        FEN+=" "+["b","w"][self.current_turn]+" "
        castling_symbols = ["K", "Q", "k", "q"]
        castles = reversed(self.to_string(self.board.piece_list).split("__")[2].split("_")[0])
        hyphen = True
        for i, j in enumerate(castles):
            if int(j) == 1:
                FEN += castling_symbols[i]
                hyphen = False
        if hyphen:
            FEN += "-"
        en_passant = False
        for piece in [p for p in self.board.piece_list if type(p) == Pawn]:
            if piece.en_passantable:
                letters = ["a", "b", "c", "d", "e", "f", "g", "h"]
                FEN += " "+letters[piece.x]+str(piece.y)+" "
                en_passant = True
                break
        if not en_passant:
            FEN += " - "
        FEN += str(min(self.moves_since_lc, self.moves_since_lpm))+" "+str(self.full_moves)
        return FEN

    def loop(self):
        while self.running:
            done = False
            while not done and self.running:
                os.system("clear")
                print(self.pc_pl[self.player_types[0]]+" VS "+self.pc_pl[self.player_types[1]])
                print("MOVE "+str(self.full_moves))
                self.board.draw()
                self.to_FEN(self.board.piece_list)
                if self.checkcheckmatestalemate(self.current_turn):
                    if self.check(self.current_turn):
                        self.endgame(self.players[(self.current_turn+1)%2]+" won by checkmate.")
                    else:
                        self.endgame("Draw by stalemate.")
                if self.checkinsufficientmaterial():
                    self.endgame("Draw by insufficient material.")
                #check for draw by repetition
                if self.checkdrawbyrep():
                    self.endgame("Draw by repetition.")
                if self.checkdrawby50moverule():
                    self.endgame("Draw by 50 moves without pawn moves or captures.")
                if self.running:
                    print(self.players[self.current_turn]+" to move.")
                    if self.check(self.current_turn):
                        print(self.players[self.current_turn]+"\'s king is in check.")
                    #for j in self.game:
                        #print(", ".join([i.letter+str(i.x)+str(i.y) for i in j]))
                    if self.player_types[self.current_turn] == 1:
                        move = input("> ")
                        if move.upper() == "Q" or move.upper() == "QUIT":
                            n = choices.alt_choice("Do you want to save the game before quitting?", ["Yes", "No"])
                            if n == 0:
                                save_game(self)
                            self.running = False
                            break
                        if move.upper() == "SAVE" or move.upper() == "S":
                            save_game(self)
                            continue
                        if move.upper() == "FLIP" or move.upper() == "F":
                            self.board.flip()
                            continue
                        if move.upper() == "RESIGN":
                            self.endgame(self.players[(self.current_turn+1)%2]+" won by resignation.")
                            break

                    else:
                        print("Stockfish is thinking...")
                        FEN = self.to_FEN(self.board.piece_list)
                        board = chess.Board(FEN)
                        result = self.fish.play(board, chess.engine.Limit(depth=self.fish.depth))
                        if result.resigned:
                            self.endgame(self.players[(self.current_turn+1)%2]+" won by resignation.")
                            break
                        else:
                            pnt("NO REESIGN")
                            move = board.san(result.move)
                        print("Stockfish played "+move)
                    board_copy = copy.deepcopy(self.board.piece_list)
                    taken_copy = copy.deepcopy(self.board.taken_pieces)
                    pieces, square, promotion_piece, conditions = parser.parse(move, self.board, self.current_turn)
                    if "long_castle" in conditions or "short_castle" in conditions:
                        if self.attempt_move(None, square, True, promotion_piece, conditions=conditions):
                            done = True
                    if "promotion" in conditions:
                        for p in pieces:
                            if self.attempt_move(p, square, True, promotion_piece, conditions=conditions):
                                if "take" in conditions:
                                    self.take(square)
                                self.promote(p, promotion_piece, square)
                                done = True
                                break
                    if pieces != [] and square != None:
                        #print(pieces)
                        #time.sleep(2)
                        if len(pieces) == 1:
                            if self.attempt_move(pieces[0], square, promotion_piece, True, conditions=conditions) == "en passant":
                                self.take([square[0], square[1]+[1,-1][self.current_turn]])
                                pieces[0].move(square)
                                done = True
                            if self.attempt_move(pieces[0], square, promotion_piece, True, conditions=conditions):
                                self.take(square)
                                pieces[0].move(square)
                                done = True
                        else:
                            candidates = []
                            for piece in pieces:
                                if self.attempt_move(piece, square, promotion_piece, True, conditions=conditions):
                                    candidates.append(piece)
                            """if len(candidates) >= 2 or len(candidates) == 0:
                                print("\b", end="\b")
                            else:
                                self.take(square)
                                candidates[0].move(square)
                                done = True"""
                            succ = []
                            if len(candidates) > 1:
                                for c in candidates:
                                    s = [c.x, c.y]
                                    piece_to_take = None
                                    for piece in self.board.piece_list:
                                        if [piece.x, piece.y] == square:
                                            piece_to_take = piece
                                    self.take(square)
                                    c.move(square)
                                    if not self.check(self.current_turn):
                                        c.move(s)
                                        c.moved = False
                                        succ.append(c)
                                    else:
                                        c.move(s)
                                        c.moved = False
                                    if piece_to_take != None:
                                        self.board.piece_list.append(piece_to_take)
                                        self.board.taken_pieces[(self.current_turn + 1) % 2].remove(piece_to_take)
                                if len(succ) == 1:
                                    for piece in self.board.piece_list:
                                        if piece.letter == succ[0].letter and [piece.x, piece.y] == [succ[0].x, succ[0].y]:
                                            self.take(square)
                                            piece.move(square)
                                            done = True
                                else:
                                    done = False
                            elif len(candidates) == 1:
                                self.take(square)
                                candidates[0].move(square)
                                done = True

                    if done:
                        if self.check(self.current_turn):
                            self.board.piece_list = board_copy
                            self.board.taken_pieces = taken_copy
                            done = False
                        if self.board.piece_list == board_copy:
                            done = False
                    #time.sleep(3)
                    if not done:
                        print("Illegal move!")
                        time.sleep(0.75)
            if done:
                for piece in self.board.piece_list:
                    if type(piece) == Pawn and piece.color == (self.current_turn + 1) % 2:
                        piece.en_passantable = False
                self.moves_since_lc += 1
                self.moves_since_lpm += 1
                if len(pieces) > 0 and type(pieces[0]) == Pawn:
                    self.moves_since_lpm = 0
                if "take" in conditions:
                    self.moves_since_lc = 0
                self.current_turn = (self.current_turn + 1) % 2
                if self.current_turn == 1:
                    self.full_moves += 1
                self.game.append(self.to_string(self.board.piece_list))
                self.board.material_imbalance = sum([p.value * [-1, 1][p.color] for p in self.board.piece_list])


def pnt(message):
    print(message)
    time.sleep(0.3)

def get_settings():
    os.system("clear")
    with open("settings.txt") as f:
        data = json.load(f)
    return data
    #choices.alt_choice("Settings", [d+": "+str(data[d]) for d in data])

def new_game():
    os.system("clear")
    c = choices.alt_choice("New game", ["Player VS Player", "Player VS Computer", "Computer VS Computer"])
    conf = [pvp,pvc,cvc][c]()
    print(conf)
    board = Board()
    if conf == [1, 0]:
        board.flipped = True
    game_manager = GameManager(board, conf)
    game_manager.loop()
    if 0 in conf:
        game_manager.fish.quit()
        for fish in game_manager.cpus:
            fish.quit()

def pvp():
    return [1, 1]

def create_fish():
    fish = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")
    return fish

def pvc():
    choice = choices.alt_choice("Choose side to play.", ["White", "Black", "Random"])
    if choice == 0 or choice == 1:
        conf = [[0, 1],[1, 0]][choice]
    else:
        conf = random.choice([[1, 0], [0, 1]])
    return conf

def cvc():
    print("Enjoy the show!")
    time.sleep(2)
    return [0, 0]

def save_game(game_manager):
    text_file = choices.text_file_input("Name the position.")
    with open(os.getcwd()+"/saved_positions/"+text_file, "a") as f:
        f.write(game_manager.game[-1])
    print("Position saved.")
    time.sleep(1)

def choose_saved_game():
    files = []
    for file in os.listdir(os.getcwd()+"/saved_positions"):
        if file.endswith(".txt"):
            files.append(file)
    if len(files) == 0:
        print("No games were found.")
        input()
    else:
        ordered_files = sorted(files, key=str.lower)
        n = choices.alt_choice("Choose a game or type \"quit\" to quit. \nThe following games were found:", [file[:-4] for file in ordered_files])
        if n == -1:
            return False
        else:
            return ordered_files[n]
        with open(os.getcwd()+"/saved_positions/"+ordered_files[n], "r") as f:
            return f.read()

def load_game():
    os.system("clear")
    print("Load game\n")
    file = choose_saved_game()
    if file != False:
        with open(os.getcwd()+"/saved_positions/"+file, "r") as f:
            p_string = f.read()
        c = choices.alt_choice("Choose players.", ["Player VS Player", "Player VS Computer", "Computer VS Computer"])
        conf = [pvp,pvc,cvc][c]()
        board = Board(pos_string = p_string)
        if conf == [1, 0]:
            board.flipped = True
        game_manager = GameManager(board, conf, pos_string = p_string)
        game_manager.loop()

def delete_game():
    os.system("clear")
    print("Delete game\n")
    file = choose_saved_game()
    if file != False:
        os.remove(os.getcwd()+"/saved_positions/"+file)
        print("Game \""+file[:-4]+"\" was deleted.")
        delete_game()

def main():
    """print(test.x)
    print(test.y)
    print(test.allowed_moves)
    test.move(1, 1)"""
    os.system("clear")
    print("""
 \u001b[38;5;46m _____  _____  _____  __    __  ___  _    _  _____  _
 \u001b[38;5;47m|__ __|| ____|| ___ ||  \  /  ||_ _|| \  | || ___ || |
 \u001b[38;5;48m  | |  | |__  | |_| || |\\\//| | | | |  \ | || |_| || |
 \u001b[38;5;49m  | |  |  __| |   __|| | \/ | | | | | |\\\| ||  _  || |
 \u001b[38;5;50m  | |  | |___ | |\ \ | |    | |_| |_| | \  || | | || |__
 \u001b[38;5;51m  |_|  |_____||_| \_\|_|    |_||___||_|  \_||_| |_||____|
 \u001b[38;5;46m _____  _   _  _____  _____  _____
 \u001b[38;5;47m| ____|| | | || ____|| ____|| ____|        _|\_
 \u001b[38;5;48m| |    | |_| || |__  | |___ | |___        / ^  \\
 \u001b[38;5;49m| |    |  _  ||  __| |____ ||____ |      |_/|   |
 \u001b[38;5;50m| |___ | | | || |___  ___| | ___| |       _/    |
 \u001b[38;5;51m|_____||_| |_||_____||_____||_____|      |_______|
 \u001b[0m
Version 1.0
Erik Kjellberg 2020""")
    alts = ["New game", "Load game", "Delete a saved game", "Settings", "Quit"]
    settings = Settings()
    result = choices.alt_choice("", alts, responses=[new_game, load_game, delete_game, get_settings, quit])
    # print(" ".join(chr(i) for i in range(9818, 9824)))
    main()

main()
