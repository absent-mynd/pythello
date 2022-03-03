from pythello import ReversAI
from graphics import *
from reversAI_agents import RandomAgent, AlphaBetaAgent
import time

def pointInBoundingBox(point, p1, p2):
    return point.getX() >= p1.getX() and point.getX() < p2.getX() and point.getY() >= p1.getY() and point.getY() < p2.getY()

def initWindow(dimX, dimY, rows, cols):
    win = GraphWin('ReversAI', dimX, dimY, autoflush=False)
    displayGridBlackStones = []
    displayGridWhiteStones = []
    displayGridBlackMoves = []
    displayGridWhiteMoves = []
    rows = rows
    cols = cols
    stepX = dimX / cols
    stepY = dimY / rows

    for row in range(rows):
        displayGridBlackStones.append([])
        displayGridWhiteStones.append([])
        displayGridBlackMoves.append([])
        displayGridWhiteMoves.append([])
        for col in range(cols):
            square = Rectangle(Point(stepX * col, stepY * row), Point(stepX * (col + 1), stepY * (row + 1)))
            square.setFill("green")
            square.setOutline("darkgreen")
            square.setWidth(5)
            square.draw(win)

            stoneB = Circle(Point(stepX * (col + .5), stepY * (row + .5)), min(stepX, stepY)/2.3)
            stoneB.setWidth(0)
            stoneB.setFill("black")
            stoneB.drawn = False
            displayGridBlackStones[row].append(stoneB)

            stoneW = Circle(Point(stepX * (col + .5), stepY * (row + .5)), min(stepX, stepY)/2.3)
            stoneW.setWidth(0)
            stoneW.setFill("white")
            stoneW.drawn = False
            displayGridWhiteStones[row].append(stoneW)
            
            moveB = Circle(Point(stepX * (col + .5), stepY * (row + .5)), min(stepX, stepY)/4)
            moveB.setOutline("black")
            moveB.setFill("green")
            moveB.setWidth(5) 
            moveB.drawn = False  
            displayGridBlackMoves[row].append(moveB)

            moveW = Circle(Point(stepX * (col + .5), stepY * (row + .5)), min(stepX, stepY)/4)
            moveW.setOutline("white")
            moveW.setFill("green")
            moveW.setWidth(5)   
            moveW.drawn = False
            displayGridWhiteMoves[row].append(moveW)
    win.update()
    return {
        "win":win, 
        "stonesB":displayGridBlackStones, 
        "stonesW":displayGridWhiteStones, 
        "movesB":displayGridBlackMoves, 
        "movesW":displayGridWhiteMoves
    }
            
def updateWindow(displayObject, position, drawValidMoves):
    grid = position.grid
    win = displayObject["win"]
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            mb = displayObject["movesB"][row][col]
            mw = displayObject["movesW"][row][col]
            if mb.drawn:
                mb.undraw()
                mb.drawn = False
            if mw.drawn:
                mb.undraw()
                mb.drawn = False

            sb = displayObject["stonesB"][row][col]
            sw = displayObject["stonesW"][row][col]
            if grid[row][col] == 0:
                if sb.drawn:
                    sb.undraw()
                    sb.drawn = False
                if sw.drawn:
                    sw.undraw()
                    sw.drawn = False
            if grid[row][col] == 1:
                if not sb.drawn:
                    sb.draw(win)
                    sb.drawn = True
                if sw.drawn:
                    sw.undraw()
                    sw.drawn = False
            if grid[row][col] == 2:
                if sb.drawn:
                    sb.undraw()
                    sb.drawn = False
                if not sw.drawn:
                    sw.draw(win)
                    sw.drawn = True

        if (drawValidMoves):
            movesArray = displayObject["movesB"] if position.color == 1 else displayObject["movesW"]
            for move in position.validMoves:
                if not move.isPassMove():
                    indicator = movesArray[move.row][move.col]
                    if not indicator.drawn:
                        indicator.draw(win)
                        indicator.drawn = True
    win.update()

def getInput(displayObject, position):
    validMoveIndicators = []
    win = displayObject["win"]
    movesArray = displayObject["movesB"] if position.color == 1 else displayObject["movesW"]
    for move in position.validMoves:
        if not move.isPassMove():
            indicator = movesArray[move.row][move.col]
            if not indicator.drawn:
                indicator.draw(win)
            validMoveIndicators.append(indicator)
    win.update()
    
    click = win.getMouse()
    if len(position.validMoves) == 1:
        if move.isPassMove():
            return move
    while True:
        for i in range(len(validMoveIndicators)):
            if pointInBoundingBox(click, validMoveIndicators[i].getP1(), validMoveIndicators[i].getP2()):
                for indicator in validMoveIndicators:
                    indicator.undraw()
                    indicator.drawn = False
                win.update()
                return position.validMoves[i]
        click = win.getMouse()

def main():
    game = ReversAI(30, 30)
    moveList = []
    instance = game.newPos()
    instance.initializeBoardOthello()

    dimX = 2000
    dimY = 2000
    display = initWindow(dimX, dimY, game.rows, game.cols)

    agent = AlphaBetaAgent(3)
    agentColor = 1

    while True:
        while not instance.gameOver:
            #instance.print()
            if (instance.color == agentColor):
                newMove = agent.selectMove(instance)
            else:
                newMove = agent.selectMove(instance)
                
            if newMove:
                moveList.append(newMove)
                instance.doMove(newMove)
            
            updateWindow(display, instance, True)
            #time.sleep(.01)
        
        while moveList:
            undo = moveList.pop()
            instance.undoMove(undo)
            updateWindow(display, instance, False)
    

if __name__ == "__main__":
   main()    