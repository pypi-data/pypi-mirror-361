

class Piece():

    def __init__(self, location, isWhite):
        self.location = location 
        self.isWhite = isWhite


    def possibleMoves(self, board):
        raise NotImplementedError("Must be implemented by the subclass") 
    
   



class Pawn(Piece):
    def __init__(self, location, isWhite):
        super().__init__(location, isWhite)  

        self.value = 100
        self.table = [ 0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 35, 35, 10,  5,  5,
        0,  0,  0, 30, 30,  0,  0,  0,
        5, -5,-10,  0,  0,-10, -5,  5,
        5, 10, 10,-20,-20, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0]

        if (location[1] == 1 and isWhite) or (location[1] == 6 and not isWhite):
            self.hasMoved = False
        else:
            self.hasMoved = True

        if isWhite: 
            self.ascii = "♟"
            self.direction = 1
        else: 
            self.ascii = "♙"
            self.direction = -1
    
    def possibleMovesAttacking(self, board):  #only squares that are attacked, useful for checks
        attacking = []

        attacking.append((self.location[0] + 1 , self.location[1] + self.direction))
        attacking.append((self.location[0] - 1 , self.location[1] + self.direction))

        return attacking
    

    def possibleMoves(self, board): 

        possible = [] 

        #Scan y+1
        move = ((self.location[0]), (self.location[1] + self.direction))
        if board.scan(move, self.isWhite) == 1:
            possible.append(move)

        #Scan y+2
        if not self.hasMoved:
            move = ((self.location[0]), (self.location[1] + self.direction*2))
            if board.scan(move, self.isWhite) == 1 and board.scan((move[0], move[1] + self.direction * -1), self.isWhite) == 1:
                possible.append("doubleMove") #This is done to account for en Passant


        #Scan diagonal capturing, towards right
        move = (self.location[0] + 1 , self.location[1] + self.direction)
        if board.scan(move, self.isWhite) == -1:
            possible.append(move)
        
        #Scan diagonal capturing, towards left
        move = (self.location[0] - 1 , self.location[1] + self.direction)
        if board.scan(move, self.isWhite) == -1:
            possible.append(move)


        #En passant
        if (board.enPassant[0] == True) and (board.enPassant[1] == (self.location[0] + 1, self.location[1]) or board.enPassant[1] == (self.location[0] -1, self.location[1])):
            possible.append("enPassant")

        return possible
            


class Knight(Piece): 
    def __init__(self, location, isWhite):
        super().__init__(location, isWhite)   
        self.value = 320
        self.table = [-50,-40,-30,-30,-30,-30,-40,-50,
-40,-20,  0,  0,  0,  0,-20,-40,
-30,  0, 10, 15, 15, 10,  0,-30,
-30,  5, 15, 20, 20, 15,  5,-30,
-30,  0, 15, 20, 20, 15,  0,-30,
-30,  5, 10, 15, 15, 10,  5,-30,
-40,-20,  0,  5,  5,  0,-20,-40,
-50,-40,-30,-30,-30,-30,-40,-50]

        if isWhite: 
            self.ascii = "♞"
        else: 
            self.ascii = "♘"   
        
    def possibleMoves(self, board):
        possible = []
        map = [(2, 1),(-2, 1), (2, -1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)]
        for i in map:
            move = ((self.location[0] + i[0]), (self.location[1] + i[1]))
            conditional = board.scan(move, self.isWhite)
            if conditional == 1 or conditional == -1:
                possible.append(move)

        return possible
                 



class Bishop(Piece):
    def __init__(self, location, isWhite):
        super().__init__(location, isWhite)
        self.table = [-20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20]
        
        self.value = 330
        if isWhite: 
            self.ascii = "♝"
        else: 
            self.ascii = "♗" 
    def possibleMoves(self, board):
        possible = [] 

        for i in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            for j in range(1, 7):
                move =  ((self.location[0] + (j*i[0])), (self.location[1] + (j * i[1])))
    
    
                conditional = board.scan(move, self.isWhite)
                if conditional == 1:
                    possible.append(move)
                elif conditional == -1:
                    possible.append(move)
                    break
                else:
                    break

        return possible

        

class King(Piece):
    def __init__(self, location, isWhite):
        super().__init__(location, isWhite)
        self.value = 20000
        self.table = [-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-20,-30,-30,-40,-40,-30,-30,-20,
-10,-20,-20,-20,-20,-20,-20,-10,
 20, 20,  0,  0,  0,  0, 20, 20,
 20, 30, 10,  0,  0, 10, 30, 20]
        if isWhite: 
            self.ascii = "♚"
            self.hasMoved = False if location == (4, 0) else True
        else: 
            self.ascii = "♔" 
            self.hasMoved = False if location == (4, 7) else True
  
    
    def attackingSquares(self, board):
        
        squares = []
        map = [(0, 1),(0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0)]
        for i in map:
            move = ((self.location[0] + i[0]), (self.location[1] + i[1]))
            conditional = board.scan(move, self.isWhite)
            if conditional == 1 or conditional == -1:
                squares.append(move)
        return squares

    #Currently, this is so disguting. I swear ill fix it soon enough
    def canCastle(self, board):

       
        castles = []
        squares = board.attackingSquares(self.isWhite)

        if self.hasMoved or self.location in squares:
            return castles
        
        y = 0 if self.isWhite else 7

        importantSquares = [  #This contain the squares that must be empty as well as the rook square [0] is for shory castling, [1] for long

        [[(5, y), (6, y)], (7, y), "0-0"],
        [[(3, y), (2, y), (1, y)], (0, y), "0-0-0"]

        ]
    
        
        #Loop through both types of castling (i.e 2 times)
        for castlingType in importantSquares:
            break_outer_loop = False  

            #Will make sure square is empty, if its not, it will try long castling
            for square in castlingType[0]:
                if board.scan(square, self.isWhite) != 1 or square in squares:
                    break_outer_loop = True
                    break
            if break_outer_loop:
                continue
            
            
            #Will make sure the correspondant rook exists
            for p in board.pieces:
                if p.location == castlingType[1] and p.__class__.__name__ == "Rook":
                    if not p.hasMoved:
                        castles.append(castlingType[2])
                    
        return castles
                        

    def possibleMoves(self, board):
        possible = []
        possible += self.attackingSquares(board)
        possible += self.canCastle(board)
        return possible


        
class Queen(Piece): 
    def __init__(self, location, isWhite):
        self.value = 900
        self.table = [-20,-10,-10, -5, -5,-10,-10,-20,
-10,  0,  0,  0,  0,  0,  0,-10,
-10,  0,  5,  5,  5,  5,  0,-10,
 -5,  0,  5,  5,  5,  5,  0, -5,
  0,  0,  5,  5,  5,  5,  0, -5,
-10,  5,  5,  5,  5,  5,  0,-10,
-10,  0,  5,  0,  0,  0,  0,-10,
-20,-10,-10, -5, -5,-10,-10,-20]
        super().__init__(location, isWhite)
        if isWhite: 
            self.ascii = "♛"
        else: 
            self.ascii = "♕"
    def possibleMoves(self, board):
        # This just borrows code from the rook and bishop

        possible = []

        #Bishop code
        for i in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            for j in range(1, 8):
                move =  ((self.location[0] + (j*i[0])), (self.location[1] + (j * i[1])))
   
                conditional = board.scan(move, self.isWhite)
                if conditional == 1:
                    possible.append(move)
                elif conditional == -1:
                    possible.append(move)
                    break
                else:
                    break

        #Rook code
        for i in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            for j in range(1, 8):
                move =  ((self.location[0] + (j*i[0])), (self.location[1] + (j * i[1])))
                conditional = board.scan(move, self.isWhite)
                if conditional == 1:
                    possible.append(move)
                elif conditional == -1:
                    possible.append(move)
                    break
                else:
                    break
        return possible



class Rook(Piece): 
    def __init__(self, location, isWhite):
        super().__init__(location, isWhite)   
        self.value = 500
        self.table = [0,  0,  0,  0,  0,  0,  0,  0,
  5, 10, 10, 10, 10, 10, 10,  5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
 -5,  0,  0,  0,  0,  0,  0, -5,
  0,  0,  0,  5,  5,  0,  0,  0]
        if isWhite: 
            self.ascii = "♜"
        else: 
            self.ascii = "♖"
        self.hasMoved = False
    def possibleMoves(self, board):       
        possible = [] 
        for i in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            for j in range(1, 8):
                move =  ((self.location[0] + (j*i[0])), (self.location[1] + (j * i[1])))
                conditional = board.scan(move, self.isWhite)
                if conditional == 1:
                    possible.append(move)
                elif conditional == -1:
                    possible.append(move)
                    break
                else:
                    break
        
        return possible        
                
        



class Board(): 
    def __init__(self, pieces, doesWhitePlay):
        self.pieces = pieces
        self.doesWhitePlay = doesWhitePlay
        self.enPassant = [False, None] #Will store the pawn that can currently be captured ith enPessant, and the color of that square
        self.checkMate = [False, None] # # checkMate[1] will store the color piece that is in checkmate
        self.staleMate = False

    def move(self, piece, square):

        previousState = {
        "piece": piece, 
        "pieceLocation": piece.location,
        "capturedPiece": None,
        "enPassant": self.enPassant[:], 
        "hasMoved": piece.hasMoved if hasattr(piece, "hasMoved") else None, 
        "promotion": [False, None], # promotion[1] will store the queen
        "castle": [False, None, None],  # castle[1] will store the rook that moved, castle[2] the type of castling
        "checkMate": self.checkMate[:], 
        "staleMate": self.staleMate

    }


        self.enPassant[0] = False

        #Check if a piece has been captured, and removes it in the case
        for p in self.pieces:
            if p.location == square:
                previousState["capturedPiece"] = p
                self.pieces.remove(p)

        if piece.__class__.__name__ == "Pawn":
        
            if not piece.hasMoved:
                piece.hasMoved = True

                if square == "doubleMove":
                    square = (piece.location[0], piece.location[1] + (piece.direction * 2))
                    self.enPassant[1] = square
                    self.enPassant[0] = True

            elif square[1] == 0 or square[1] == 7:
                previousState["promotion"][0] = True

                new = Queen(square, piece.isWhite)

                for p in self.pieces:
                    if p.location == piece.location and p.isWhite == piece.isWhite and p.__class__ == piece.__class__:
                        self.pieces.remove(p)

                previousState["promotion"][1] = new
                self.pieces.append(new)

            elif square == "enPassant":

                #The square to which the pawn will move to
                square = (self.enPassant[1][0], self.enPassant[1][1] + piece.direction)

                #Removing the other pawn
                for p in self.pieces:
                    if p.location == self.enPassant[1]:
                        previousState["capturedPiece"] = p
                        self.pieces.remove(p)


        elif  piece.__class__.__name__ == "King" or  piece.__class__.__name__ == "Rook": 
            if piece.hasMoved == False:
                piece.hasMoved = True  

            if square == "0-0":


                y = 0 if piece.isWhite else 7

                square = (6, y)

                #Search for rook and place it accordingly
                for p in self.pieces:
                    if p.location == (7, y):
                        p.location = (5, y)
                        previousState["castle"][1] = p

                previousState["castle"][0] = True
                
                previousState["castle"][2] = "0-0"

            elif square == "0-0-0":
                y = 0 if piece.isWhite else 7

                square = (2, y)

                #Search for rook and place it accordingly
                for p in self.pieces:
                    if p.location == (0, y):
                        p.location = (3, y)
                        previousState["castle"][1] = p

                previousState["castle"][0] = True
                
                previousState["castle"][2] = "0-0-0"



                
        self.doesWhitePlay = not self.doesWhitePlay
        piece.location = square
        return previousState

    def undoMove(self, previousState):
        piece = previousState["piece"]

        self.checkMate = previousState["checkMate"]
        self.staleMate = previousState["staleMate"]
        
        if previousState["hasMoved"] != None:
            piece.hasMoved = previousState["hasMoved"]
        if previousState["capturedPiece"]:
            self.pieces.append(previousState["capturedPiece"])
        
        if previousState["promotion"][0]:
            #Remove the queen
            self.pieces.remove(previousState["promotion"][1])

            self.pieces.append(piece)
        
        if previousState["castle"][0]:
            y = 0 if piece.isWhite else 7
            if previousState["castle"][2] == "0-0":
                #Returning rook to proper place
                previousState["castle"][1].location = (7, y)
                previousState["castle"][1].hasMoved = False

            else: #Long castle
                #Returning rook to proper place
                previousState["castle"][1].location = (0, y)
                previousState["castle"][1].hasMoved = False




        self.enPassant = previousState["enPassant"]
        self.doesWhitePlay = not self.doesWhitePlay
        piece.location = previousState["pieceLocation"]
        

    def draw(self): 
        board = []
        for i in range(8):
            board.append([])
            for j in range(8):
                board[i].append("[ ]")
                
        for piece in self.pieces:
            board[piece.location[0]][piece.location[1]] = f"[{piece.ascii}]"
        

        #Now, draw:
        for i in range(7, -1, -1):
            stringy = ""
            for j in range(8):
                stringy += board[j][i]
            print(f"{i} " + stringy)
        print("   0  1  2  3  4  5  6  7 ")

    
    def checkOrStailMate(self): #this method works to assist the possibleMoved method. PLEASE do not use it indepently
        if self.isInCheck(self.doesWhitePlay):
            self.checkMate[0] = True
            self.checkMate[1] = self.doesWhitePlay
            return "CHECKMATE"
        
        else:
            self.staleMate = True
            return "STALEMATE"
    
    #Return a dictionary with the piece object, and a list where such piece can move
    def possibleMoves(self):
        legalMoves = False

        possible = {}
        pieces = self.pieces[:]
        
        for piece in pieces:
            moves =  []
            if piece.isWhite == self.doesWhitePlay:
                for move in piece.possibleMoves(self):

                    previousState = self.move(piece, move)
                    
                    if not self.isInCheck(not self.doesWhitePlay):
                        moves.append(move)
                        legalMoves = True

                    self.undoMove(previousState)
                    
            else: 
                continue

            possible[piece] = moves
    
        if not legalMoves:
            return self.checkOrStailMate() 
                   
        return possible
    
    
    #Scan if a square is empty and possible in the board. 
    # 1: its empty; -2: its occupied by a piece of the same color; -1: occupied by an enemy piece
    def scan(self, square, isWhite):

        #Scan if a square is in bounds
        if not (square[0] <= 7 and square[0] >= 0 and square[1] <= 7 and square[1] >= 0):
            return 0

        #Scan if the square is empty
        for piece in self.pieces: 
            if piece.location == square:
                if isWhite == piece.isWhite:
                    return -2
                else: 
                    return -1                

   
   
   
        return 1    
    
    #Will check if that the king cannot be captured with a given move 
    def isInCheck(self, isWhite):
        king = None
        attackedSquares = []
        for p in self.pieces:
            if  p.__class__.__name__ == "King" and p.isWhite == isWhite:
                king = p
                
                break
        
        attackedSquares = self.attackingSquares(isWhite)

        if king.location in attackedSquares:
            return True
        else:
            return False
        
    def attackingSquares(self, isWhite):
        attackedSquares = []

        for p in self.pieces:
            if p.isWhite != isWhite:
                    if p.__class__.__name__ == "Pawn":
                        attackedSquares += p.possibleMovesAttacking(self)
                    elif p.__class__.__name__ == "King":
                        attackedSquares += p.attackingSquares(self)
                    else:
                        attackedSquares += p.possibleMoves(self)
        
        return attackedSquares




#A function that will take a fen as input, and create a respective board
def FEN(fen, doesWhitePlay):
    x = 0
    y = 7
    pieces = []
    for char in fen: 
        is_int = False
        if char.isupper():
            char = char.lower()
            isWhite = True
        else: 
            isWhite = False

    

        match char:
            case 'p':
                piece = Pawn((x, y), isWhite)
                x += 1
            case 'q':
                piece = Queen((x, y), isWhite) 
                x += 1
            case 'k':
                piece = King((x, y), isWhite)
                x +=1
            case 'n':
                piece = Knight((x, y), isWhite)
                x += 1
            case 'r':
                piece = Rook((x, y), isWhite)
                x += 1
            case 'b':
                piece = Bishop((x, y), isWhite)
                x += 1
            case '/':
                is_int = True
                y -= 1
                x = 0 

            case _:  # It has to be an int
                is_int = True
                char = int(char)
                x += char

        if not is_int:
            pieces.append(piece)

    return Board(pieces, doesWhitePlay)
    



#Simple eval function lol
def evaluate(board, depth):
    eval = 0
    
    for piece in board.pieces:
        if piece.isWhite:
            index = piece.location[0] + ((7-(piece.location[1])) * 8)
            eval += piece.value
            eval += piece.table[index]

        else:
            index = piece.location[0] + piece.location[1] * 8 
            eval -= piece.value
            eval -= piece.table[index]

   
    possible = board.possibleMoves()
    
    if board.checkMate[0]:

        eval = -1000000 - depth*100 if board.checkMate[1] else 1000000 + depth*100
        

    return eval



def possiblePositions(board, depth):
    total = 0
    
    possible = board.possibleMoves()
    if depth == 0 or possible == "CHECKMATE" or possible == "STALEMATE":
        return 1
   

    for piece in possible:
        for move in possible[piece]:

            previousMove = board.move(piece, move)

            total += amountOfMoves(board, depth-1)

            board.undoMove(previousMove)

    return total



def minimaxImproved(board, depth, alpha=-1000, beta=1000):
    possible = board.possibleMoves()

    if depth == 0 or possible == "CHECKMATE" or possible == "STALEMATE":
        return evaluate(board, depth)

    if board.doesWhitePlay:
        best = -1000
        for piece in possible:
            for move in possible[piece]:
                lastMove = board.move(piece, move)
                score = minimaxImproved(board, depth - 1, alpha, beta)
                board.undoMove(lastMove)

                best = max(best, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    return best  # Beta cut-off
        return best

    else:
        best = 1000
        for piece in possible:
            for move in possible[piece]:
                lastMove = board.move(piece, move)
                score = minimaxImproved(board, depth - 1, alpha, beta)
                board.undoMove(lastMove)

                best = min(best, score)
                beta = min(beta, score)
                if beta <= alpha:
                    return best  # Alpha cut-off
        return best

#MINIMAX
def minimax(board, depth):


    possible = board.possibleMoves()

    if depth == 0 or possible == "CHECKMATE" or possible == "STALEMATE":
        return evaluate(board, depth)
    
    if board.doesWhitePlay:
        best = -1000

        for piece in possible:
            for move in possible[piece]:
                lastMove = board.move(piece, move)
                score = minimax(board, depth-1)
                board.undoMove(lastMove)
                if score > best:
                    best = score    
              

    else:
        best = 1000

        for piece in possible:
            for move in possible[piece]:
                lastMove = board.move(piece, move)
                score = minimax(board, depth-1)
                board.undoMove(lastMove)
                if score < best:
                    best = score    

            

    return best





def bestMove(board, depth):
    bestMove = None
    bestEval = float('-inf') if board.doesWhitePlay else float('inf')
    possible = board.possibleMoves()

    if possible == "CHECKMATE" or possible == "STALEMATE":
        return None

    for piece in possible:
        for move in possible[piece]:
            lastMove = board.move(piece, move)
            eval = minimaxImproved(board, depth - 1)
            board.undoMove(lastMove)
            

            if board.doesWhitePlay:
                if eval > bestEval:
                    bestEval = eval
                    bestMove = (piece, move)
            else:
                if eval < bestEval:
                    bestEval = eval
                    bestMove = (piece, move)

    return bestMove
                




def play():
    myBoard = FEN("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", True) 
    print("Welcome to SailMate!, lets play some chess!") 
    depth = input("Please enter the depth of the AI (default is 2), more and it becomes quite slow: ")
    print(f"AI will play with a depth of {depth if depth.isdigit() else 2} moves ahead")

    playerColor = input("Do you want to play as white or black? (w/b): ").lower()
    playerColor = True if playerColor == "w" else False
    print(f"You are playing as {'White' if playerColor else 'Black'}")




    while True:
        myBoard.draw()
        if playerColor == myBoard.doesWhitePlay:
            print("Your turn to play!")
            for piece in myBoard.possibleMoves():
                print(f"{piece.ascii} at {piece.location} to {myBoard.possibleMoves()[piece]}")
            moveOrLocation = input("Enter the CURRENT location of the piece you want to move (e.g. (0, 1) ): ")
            moveLocation = input("Enter the location or move you want to move the piece to (e.g. (0, 1) or doubleMove or 0-0): ")


            moved = False
            possible = myBoard.possibleMoves()
            if possible == "CHECKMATE" or possible == "STALEMATE":
                print("Game over!, its a {possible}!")
                print("I WIN MUAHAHAH")
                return
            #search for piece
            for p in possible:
                for m in possible[p]: #for move in piece

                    if str(p.location) == moveOrLocation and str(m) == moveLocation:
                        #doable move
                        myBoard.move(p, m)
                        print("Perfect, your move was successful!")
                        moved = True
            if not moved: 
                print("Invalid move, try again!")
                continue 
            
            
        else:
            print("The IA is thinking...")
            move = bestMove(myBoard, int(depth) if depth.isdigit() else 2)
            if move is None:
                print(f"Wait... Game over!,{myBoard.checkOrStailMate()}!")
                if myBoard.checkOrStailMate() == "CHECKMATE":
                    print("YU HAVE WON")
                return
            myBoard.move(move[0], move[1])



play()



