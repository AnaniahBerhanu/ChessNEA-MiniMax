"""
THis class is responsible for storing all information about the current state of a chess game  and also be responsile for 
determing the valid moves at the current state.It will also keep a move log
"""
class GameState():
    def __init__(self):
        #board is an 8x8 2d Array each element of list has 2 charachters
        #the first charachter represents the color of the piece
        #the second character represents the type of piece e,g r is rook k is king
        #"--" repersents an empty space with no piece
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
            ]
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = () #co-ordinates for where enpassant is possible
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs,
                                              self.currentCastlingRight.bqs)]

        self.moveFunctions = {'p': self.getPawnMoves, 'R':self.getRookMoves, 'N':self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q':self.getQueenMoves, 'K': self.getKingMoves}
    """
    Takes a move and executes however will not work with castiling and en passant 
    """
    def makeMove(self,move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # logs move so we can undo it in the future
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow,move.endCol)
        elif move.pieceMoved =='bK':
            self.blackKingLocation = (move.endRow,move.endCol)
        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol]= move.pieceMoved[0] +'Q'
        #enpassant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol]= "--"
            #self.board[move.endRow + (1 if self.whiteToMove else -1)][move.endCol] = "--"
            #self.board[move.endRow][move.endCol]= move.pieceMoved
            #update enpassant possible variable 
        if move.pieceMoved[1]=="p" and abs(move.startRow - move.endRow)==2: #only for 2 square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow)//2,move.startCol)
        else:
            self.enpassantPossible = ()
        

    
        #castle move
        if move.isCastleMove:
            if move.endCol-move.startCol==2:#this would mean a king side castle as it would mean that it moved to the right
                self.board[move.endRow][move.endCol-1]= self.board[move.endRow][move.endCol+1]#moves the rook
                self.board[move.endRow][move.endCol+1]="--"#erares the rook from its old position 
            else:
                #queenside move
                self.board[move.endRow][move.endCol+1]= self.board[move.endRow][move.endCol-2]#moves rook
                self.board[move.endRow][move.endCol-2]="--"

        
        #update castling rights-whenever it is a rook or king move 
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs,
                                              self.currentCastlingRight.bqs))





    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == 'wK':
              #could be ==
              self.whiteKingLocation = (move.startRow,move.startCol)
            elif move.pieceMoved =='bK':
              self.blackKingLocation = (move.startRow,move.startCol)
            #undo en passant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol]= "--"#leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow,move.endCol)
            #undo 2 square pawn advance
            if move.pieceMoved[1]=="p" and abs(move.startRow - move.endRow) ==2:
                self.enpassantPossible = ()
            #undo castling rights
            self.castleRightsLog.pop() #get rid of new castle rights from move we are undoing
            newRights = self.castleRightsLog[-1]#set current castle rights to the last one in the list
            self.currentCastlingRight = CastleRights(newRights.wks,newRights.bks,
                                                     newRights.wqs,newRights.bqs)
            #undo castle move
            if move.isCastleMove:
                if move.endCol-move.startCol ==2:#kingside castle
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = "--"
                else:#queenside
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1]= "--"

    """
    update castle rights given the move
    """
    def updateCastleRights(self,move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow ==7:
                if move.startCol==0: #7th row and first column would be left side rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:#this would mean right side rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow ==0:
                if move.startCol==0: #0th row and first column would be left side rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:#this would mean right side rook
                    self.currentCastlingRight.wks = False



    #all moves considering checks
    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, 
                                        self.currentCastlingRight.bqs)#coppies the current castling rights
        
        
        #naive algorithm
        #1 generate all of the possible moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0],self.whiteKingLocation[1],moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0],self.blackKingLocation[1],moves)

        #2for each move make the move
        for i in range(len(moves)-1,-1,-1):#when removing we will iterate from the back of the list to the front
            self.makeMove(moves[i])
            #3 generate all opponents move
            #4for each of your oponents move see if they attack your king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i]) #5if they do attack your king then not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves)==0:#either checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
                print("Checkmate")
            else:
                self.staleMate = True
                print("stalemate")
        else:
            self.checkMate = False
            self.staleMate = False
            #return self.getAllPossibleMoves()
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves

    #determines if current player is in check
    def inCheck(self):
        #decoupling
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])
        
    
    #determines if enemy can attack the square r,c
    def squareUnderAttack(self,r,c):
        self.whiteToMove = not self.whiteToMove #switch to opponets point of view
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove #switch back
        for move in oppMoves:
            if move.endRow == r and move.endCol ==c:#square is under attack
                return True
        return False



    #all moves without considering chess
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0] #accesses the peice and then checks the first letter to see whos piece it is 
                if (turn == "w" and self.whiteToMove) or  (turn == "b" and not self.whiteToMove):
                    #will not iterate through each piece
                    piece  = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)#calls appropriate validation function
        return moves
    


    ""
    def getPawnMoves(self,r, c ,moves):
        if self.whiteToMove:
            if self.board[r-1][c] == "--":
                moves.append(Move((r,c), (r-1,c), self.board))
                if r == 6 and self.board[r-2][c] == "--":#2 square pawn advance
                    moves.append(Move((r,c),(r-2,c), self.board))
            if c-1 >= 0:#left diagonal capture
                if self.board[r-1][c-1][0] == "b": #enemy piece is there
                    moves.append(Move((r,c),(r-1,c-1), self.board))
                elif (r-1,c-1)== self.enpassantPossible:
                    moves.append(Move((r,c),(r-1,c-1),self.board, isEnpassantMove=True))
            if c+1 <= 7:
                if self.board[r-1][c+1][0] == "b":
                    moves.append(Move((r,c),(r-1,c+1), self.board))
                elif (r-1,c+1)== self.enpassantPossible:
                    moves.append(Move((r,c),(r-1,c+1),self.board, isEnpassantMove=True))
            
        else:
            if self.board[r+1][c] == "--":
                moves.append(Move((r,c),(r+1,c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r,c),(r+2,c),self.board))
            if c-1 >=0:#left diagonal capture
                if self.board[r+1][c-1][0]== "w":
                    moves.append(Move((r,c),(r+1,c-1),self.board))
                elif (r+1,c-1)==self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c-1),self.board, isEnpassantMove=True))
            if c+1 <=7:
                if self.board[r+1][c+1][0]=="w":
                    moves.append(Move((r,c),(r+1,c+1),self.board))
                elif (r+1,c+1)== self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c+1),self.board,isEnpassantMove=True))

        #i need to change this it is very bad note to self
    def getRookMoves(self,r, c ,moves):
       if self.whiteToMove:
            i=c+1
            while i <= 7 and self.board[r][i] == "--" :
                moves.append(Move((r,c),(r,i),self.board))
                i+=1
            while i<=7 and self.board[r][i][0]=="b":
                moves.append(Move((r,c),(r,i),self.board))
                break
            i=c-1
            while i>=0 and self.board[r][i]=="--":
                moves.append(Move((r,c),(r,i),self.board))
                i-=1
            while i>=0 and self.board[r][i][0]=="b":
                moves.append(Move((r,c),(r,i),self.board))
                break
            i=r+1
            while i <=7 and self.board[i][c]=="--":
                moves.append(Move((r,c),(i,c),self.board))
                i+=1
            while i<=7 and self.board[i][c][0]=="b":
                moves.append(Move((r,c),(i,c),self.board))
                break              
            i = r-1
            while i>=0 and self.board[i][c]== "--":
                moves.append(Move((r,c),(i,c),self.board))
                i-=1
            while i>=0 and self.board[i][c][0]=="b":
                moves.append(Move((r,c),(i,c),self.board))
                break
       if not self.whiteToMove:
           i=c+1
           while i<= 7 and self.board[r][i]=="--":
               moves.append(Move((r,c),(r,i),self.board))
               i+=1
           while i <=7 and self.board[r][i][0]=="w":
               moves.append(Move((r,c),(r,i),self.board))
               break
           i = c-1
           while i >=0 and self.board[r][i]=="--":
               moves.append(Move((r,c),(r,i),self.board))
               i-=1
           while i >=0 and self.board[r][i][0]=="w":
               moves.append(Move((r,c),(r,i),self.board))
               break   
           i = r+1
           while i<=7 and self.board[i][c]=="--":
               moves.append(Move((r,c),(i,c),self.board))
               i+=1
           while i<=7 and self.board[i][c][0]=="w":
               moves.append(Move((r,c),(i,c),self.board))
               break
           i=r-1
           while i >=0 and self.board[i][c]=="--":
               moves.append(Move((r,c),(i,c),self.board))
               i-=1
           while i>=0 and self.board[i][c][0]=="w":
               moves.append(Move((r,c),(i,c),self.board))
               break 


            


    def getKnightMoves(self,r, c ,moves):
        directions = ((-2,1), (-2,-1), (2,1), (2,-1), (-1,2), (-1,-2),(1,2), (1,-2))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            endRow = r +d[0]
            endCol = c +d[1]
            if 0 <= endRow <=7 and 0<= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece =="--":
                    moves.append(Move((r,c),(endRow,endCol),self.board))
                if endPiece[0] == enemyColor:
                    moves.append(Move((r,c),(endRow,endCol),self.board))



    def getBishopMoves(self,r, c ,moves):
        directions = ((1,1),(-1,-1),(-1,1),(1,-1))
        enemycolor  = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r +d[0]*i
                endCol = c +d[1]*i
                if 0<= endRow <=7 and 0<= endCol <=7:
                    endpiece = self.board[endRow][endCol]
                    if endpiece =="--":
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endpiece[0] == enemycolor:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else:#if the endpiece is not empty or enemy piece then it is our own piece which we cant jump
                        break
                else:
                    break
    

    def getQueenMoves(self,r, c ,moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)

    def getKingMoves(self,r, c ,moves):
        directions = ((-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1))
        enemyColor = "b" if self.whiteToMove else "w"
        allycolor = "w" if self.whiteToMove else 'b'
        for d in directions:
            endRow = r +d[0]
            endCol = c+d[1]
            if 0<= endRow <=7 and 0<= endCol <=7:
                endpiece =self.board[endRow][endCol]
                if endpiece == "--" or endpiece[0]==enemyColor:
                    moves.append(Move((r,c),(endRow,endCol),self.board))
        #Castling
        #self.getCastleMoves(r,c, moves, allycolor)

        
    """
    generate all valid castle moves for king and then add them to the list of move
    """
    def getCastleMoves(self,r,c,moves,):
        if self.squareUnderAttack(r,c):
            return #we can not castle in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r,c,moves,)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r,c,moves,)
    
    def getKingsideCastleMoves(self,r,c,moves):
        if self.board[r][c+1]== "--" and self.board[r][c+2]=="--":
            if not self.squareUnderAttack(r,c+1) and not self.squareUnderAttack(r,c+2):
                moves.append(Move((r,c),(r,c+2),self.board,isCastleMove = True))  

    def getQueensideCastleMoves(self,r,c,moves):
        if self.board[r][c-1]=="--" and self.board[r][c-2]=="--" and self.board[r][c-3]:
            if not self.squareUnderAttack(r,c-1) and not self.squareUnderAttack(r,c-2):
                moves.append(Move((r,c),(r,c-2),self.board,isCastleMove = True)) 
    


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs



class Move():
    #maps keys to values
    #key : value
    """
    ranks are the horizontal rows on a chessboard
    files are the vertical columns on a chessborard
    what this does is map the row to a position on our 2d array 
    e.g rank 1 is the last row on our 2d array so index 7
    """
    
    rankstoRows = { "1":7, "2":6, "3":5, "4":4, 
                   "5":3, "6":2, "7":1, "8":0
                   }
    
    rowstoRanks = {v:k for k, v in rankstoRows.items()}
    #does the reverse opertation for the last dictionary

    filesToCols = {"a":0, "b":1, "c":2, "d":3,
                   "e":4, "f":5, "g":6, "h":7
    }

    colstoFiles = {v:k for k,v in filesToCols.items()}   
    #does the reverse operation of th last dictionary

    def __init__(self,startSq,endSq, board, isEnpassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        #pawn promotion
        self.isPawnPromotion = False
        if (self.pieceMoved =='wp' and self.endRow==0) or (self.pieceMoved=='bp' and self.endRow==7):
            self.isPawnPromotion = True
        #enpassant
        self.isEnpassantMove = isEnpassantMove
        #self.isEnpassantMove = (self.pieceMoved[1]=='p' and (self.endRow, self.endCol) ==isEnpassantMove )
        if self.isEnpassantMove:
            self.pieceCaptured ='wp' if self.pieceMoved ==' bp' else 'bp'
        #if self.pieceMoved[1]=='p' and (self.endRow,self.endCol)== enpassantPossible:
            #self.isEnpassantMove = True
        #error
        #castle move
        self.isCastleMove = isCastleMove




        #print(self.moveID)
    def getRankFile(self,r,c):
        return self.colstoFiles[c] + self.rowstoRanks[r]
    
    def getChessnotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    
    #override equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
    