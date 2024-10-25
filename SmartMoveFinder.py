import random
#asigning numerical values to each piece
piceScore ={"K":0, "Q":10, "R":5,"B":3, "N":3,"p":1}
CHECKMATE = 1000
STALEMATE = 0
#for black perspective checkmate is the worst possible score 


def findRandomMove(ValidMoves):
    return ValidMoves[random.randint(0,len(ValidMoves)-1)]#gets a random move from all valid moves



def findBestMove(gs,validMoves):
    #looking to find the minimum of opponents maximum move
    #minMax algorithm
    turnMultiplier = 1 if gs.whiteToMove else -1
    #white will be aiming for the biggest score
    #black will be aiming for the smallest score
    #from black POV
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves) #to avoid getting the same move every time
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentsMoves = gs.getValidMoves()

        opponentsMaxScore = -CHECKMATE
        for opponentsMove in opponentsMoves:
            gs.makeMove(opponentsMove)
            if gs.checkMate:
                score = -CHECKMATE *CHECKMATE
            elif gs.staleMate:
                score = STALEMATE
            else:
                score = -turnMultiplier *scoreMaterial(gs.board)
            if score > opponentsMaxScore:
                opponentsMaxScore = score 
            gs.undoMove()
        if opponentsMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentsMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove
    




"""
score the board based on material
"""

def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0]=='w':
                score+= piceScore[square[1]]
            elif square[0]=='b':
                score-= piceScore[square[1]]
    return score
