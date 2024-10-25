"""
This is our main driver file and will be responsible for handling user input and displaying current game state
"""

import pygame as p
import ChessEngine
import images
import SmartMoveFinder

WIDTH = HEIGHT = 512
#could use 400
DIMENSION = 8
#chess board is 8X8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15



images = {}

"""
Initializes a  dictionary of images and will be called only once
"""
def LoadImages():
    pieces = ['wp','wR','wN','wB','wK', 'wQ','bp', 'bN', 'bB', 'bK', 'bQ', 'bR' ]
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"),(SQ_SIZE, SQ_SIZE))

#This is the main driver for our code and will handle user input and update the UI

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag variale for when a move is made
    animate = False #flag variable for when we should want to anaimate
    LoadImages() #we only need to load the images once
    running  = True
    sqSelected = ()#starts as empty as no square is selected will be a tuple data type of (row,col)
    playerClicks = []# keeps track of players clicks(two tuples: (6,4)to (44))
    gameOver = False
    playerOne = True#if a human is playing white then this will be true,if an AI playing then False
    playerTwo = True #if a human is playing black then this true but if AI playing then False

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo ) #True if a player is meant to be going and False if an Ai is meant to be going
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse event handling
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos() #gets (x,y) position of the mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row,col):
                        sqSelected = () #deselects option
                        playerClicks = [] #clears players clicks
                    else:
                        sqSelected = (row,col)
                        playerClicks.append(sqSelected) #appends for both first and second click
                    if len(playerClicks) == 2: #the move needs to be made  and this will be done in the move class in the chessengine file
                            move = ChessEngine.Move(playerClicks[0],playerClicks[1],gs.board)
                            print(move.getChessnotation())
                            for i in range(len(validMoves)):
                                if move == validMoves[i]:
                                    gs.makeMove(validMoves[i])
                                    print(move.moveID)
                                    moveMade = True
                                    animate = True
                                    sqSelected = () #reset user clicks
                                    playerClicks = [] #reset player clicks
                            if not moveMade:
                                print("ILLEGAL Move attempted") #new debug may affect old
                            #sqSelected = () # new debug may affect old
                                #playerClicks = [] # new debug may affect old
                                playerClicks = [sqSelected] #p5-21:31
            #undo move event handling
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when z is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    #this is too prevent animating enemies move when a player undos their move
                elif e.key == p.K_r:#reset the board when r is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
        
        #AI move finder logic
        if not gameOver and not humanTurn:
            AIMOVE = SmartMoveFinder.findBestMove(gs, validMoves)
            if AIMOVE is None:
                AIMOVE = SmartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMOVE)
            moveMade = True
            animate = True


        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1],screen,gs.board,clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate =False

        drawGameState(screen, gs, validMoves, sqSelected)


        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen,"Black wins by checkmate")
            else:
                drawText(screen,"White wins by checkmate")
        elif gs.staleMate:
            gameOver = True
            drawText(screen,"stalmate")
        
        #drawGameState(screen, gs, validMoves, sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()


"""
Highlight the valid moves when a piece is selected
"""

def highlightSquares(screen,gs,validMoves,sqSelected):
    if sqSelected != ():#ensuring the square selected is not empty
        r,c = sqSelected
        if gs.board[r][c][0]==('w'if gs.whiteToMove else 'b'):#checking to make sure that the colour of piece selected is that persons turn to move
            #highlight selected square
            s=p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)#0 is transparent #255 is opaque
            s.fill(p.Color('blue'))
            screen.blit(s,(c*SQ_SIZE, r*SQ_SIZE))
            #highlit valid moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol==c:
                    screen.blit(s,(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))




def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen) # draw the squares on the chess board
    highlightSquares(screen,gs,validMoves,sqSelected)
    drawPieces(screen, gs.board) # draw the individual piees and place on top of the squares

def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    #beige and grey
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color =  colors[((r+c)% 2)] #if th
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece!= "--":
                screen.blit(images[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

                #blit places a image on the pygame screen with the image being the piece

def animateMove(move,screen,board,clock):
    global colors
    coords = []#list of rows and columns that animation will move through
    #change in row change in coloumn
    dr = move.endRow - move.startRow
    dc = move.endCol - move.startCol
    framespersquare = 10 #frames to move one square
    frameCount = (abs(dr)+ abs(dc))*framespersquare
    for frame in range(frameCount +1):
        r,c =((move.startRow +dr*frame/frameCount, move.startCol + dc*frame/frameCount))
        drawBoard(screen)
        drawPieces(screen,board)
        #erase piece mvoeed from ending square
        color = colors[(move.endRow+move.endCol)%2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE,SQ_SIZE)
        p.draw.rect(screen,color,endSquare)
        #draws captured piece onto rectangle
        if move.pieceCaptured != '--':
            screen.blit(images[move.pieceCaptured],endSquare)
        #draw moving piece
        screen.blit(images[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawText(screen,text):
    font = p.font.SysFont('helvitca',32,True,False)
    #font(font,size,bold,ittalic)
    textObject = font.render(text,0,p.Color('Black'))
    textLocation = p.Rect(0,0,WIDTH,HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject,textLocation.move(2,2))



if __name__ == "__main__":
    main()

