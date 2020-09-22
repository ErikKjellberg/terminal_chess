import time

def parse(move_string, board, turn):
    pieces = ["K", "Q", "R", "B", "N", "P"]
    letters = ["a", "b", "c", "d", "e", "f", "g", "h"]
    number_strings = [str(i) for i in range(1, 9)]
    # board_letters = [[(square.letter+str(square.color)) if square != None else "" for square in row] for row in board.square_list]
    # board_letters = "\n".join("".join((square.letter+str(square.color)) if square != None else "" for square in row) for row in board.square_list)
    piece_list = []
    square = None
    conditions = []
    promotion_piece = None
    """if "x" in move_string:
        #first_piece_list = move_string[:move_string.index("x")]
        # second_piece_list = move_string[move_string.index("x")+1:]
        #piece_list = [first_piece, second_piece]
        piece_list = move_string[:move_string.index("x")]
    elif move_string[0] in pieces:
        piece_list = [move_string[0]]"""
    if len(move_string) < 2:
        return piece_list, square, promotion_piece, conditions
    if len(move_string) >= 3:
        if move_string[-1] == "+":
            conditions.append("check")
            move_string = move_string.replace("+", "")

        if move_string[-1] == "#":
            conditions.append("checkmate")
            move_string = move_string.replace("#", "")

        if move_string[-2] == "=" and move_string[-1] in pieces:
            conditions.append("promotion")
            promotion_piece = move_string[-1]
            move_string = move_string.replace("=", "")
            move_string = move_string[:-1]
    #time.sleep(4)

    if "x" in move_string and move_string.count("x") == 1 and len(move_string[move_string.index("x")+1:]) == 2:
        succeed = False
        if move_string[move_string.index("x")+1] in letters and move_string[move_string.index("x")+2] in number_strings:
            x = letters.index(move_string[move_string.index("x")+1])
            y = int(move_string[move_string.index("x")+2])-1
            print(x, y)
            for piece in board.piece_list:
                if piece.pos == [x, y]:
                    succeed = True
        if not succeed and piece.letter != "P":
            print("You didn't take anything!")
            return piece_list, square, promotion_piece, conditions
        if 1 <= len(move_string[:move_string.index("x")]) <= 3 and \
        len(move_string[move_string.index("x")+1:]) == 2:
            conditions.append("take")
            move_string = move_string.replace("x", "")
    # print("With removed x: ",move_string)
    if move_string[0] in pieces and len(move_string) >= 3:
        """if piece_list == "K":
            pass
        else:
            if board_letters.count(move_string[0]+str(turn)) > 1:
                print("More than one of the requested piece to move")
                print("Hmm what to do now...")
                # check all pieces
            elif board_letters.count(move_string[0]+str(turn)) == 1:
                print("The piece exists.")"""
        """for row in board.square_list:
            for square in row:
                if square != None:
                    if square.letter == move_string[0] and square.color == turn:
                        piece_list.append(square)
                        print(square)"""
        n = 1
        if move_string[1] in letters and move_string[2] in number_strings and len(move_string) < 5:
            for piece in board.piece_list:
                if piece.letter == move_string[0] and piece.color == turn:
                    piece_list.append(piece)
        elif move_string[1] in letters and move_string[2] in letters and move_string[3] in number_strings:
            n = 2
            for piece in board.piece_list:
                if piece.letter == move_string[0] and piece.color == turn and piece.x == letters.index(move_string[1]):
                    piece_list.append(piece)
        elif move_string[1] in number_strings and move_string[2] in letters and move_string[3] in number_strings:
            n = 2
            for piece in board.piece_list:
                if piece.letter == move_string[0] and piece.color == turn and piece.y == number_strings.index(move_string[1]):
                    piece_list.append(piece)
        elif move_string[1] in letters and move_string[2] in number_strings and move_string[3] in letters and move_string[4] in number_strings:
            n = 3
            print("HIWNE3e2")
            time.sleep(3)
            for piece in board.piece_list:
                if piece.letter == move_string[0] and piece.color == turn and piece.x == letters.index(move_string[1]) and piece.y == int(move_string[2])-1:
                    print("HIWNE")
                    time.sleep(3)
                    piece_list.append(piece)
        if move_string[n] in letters and move_string[n+1] in number_strings:
            square = [letters.index(move_string[n]), int(move_string[n+1])-1]

    elif move_string[0] in letters:
        n = None
        if move_string[1] in number_strings and len(move_string) == 2:
            n = 0
        elif "take" in conditions and move_string[1] in letters and move_string[2] in number_strings and len(move_string) == 3:
            n = 1
        #print(letters.index(move_string[0]))
        #print("YEEEE")
        """for row in board.square_list:
            for square in row:
                if square != None:
                    if square.letter == "P" and square.color == turn and square.x == letters.index(move_string[0]):
                        piece_list.append(square)"""
        for piece in board.piece_list:
            if piece.letter == "P" and piece.color == turn and piece.x == letters.index(move_string[0]):
                piece_list.append(piece)
        if n != None:
            square = [letters.index(move_string[n]), int(move_string[n+1])-1]

    elif move_string == "0-0-0" or move_string == "O-O-O":
        square = "long castle"
        conditions.append("long_castle")
    elif move_string == "0-0" or move_string == "O-O":
        square = "short castle"
        conditions.append("short_castle")

    # print("This is the found pieces: ")
    """for piece in piece_list:
        print("Piece: " + piece.letter + ", " + str(piece.pos))"""
    return piece_list, square, promotion_piece, conditions
