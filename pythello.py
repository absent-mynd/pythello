import copy

class Pythello:
    # 1 = black   2 = white
    # Black goes first

    inverseColor = [0, 2, 1]

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

    def inBounds(self, row, col):
        return row < self.rows and row >= 0 and col < self.cols and col >= 0
                        
    class Position:
        
        def __init__(self, gameInstance, color = 1, grid=[]):
            if len(grid) == 0:
                self.grid = [[0 for i in range(gameInstance.rows)] for j in range(gameInstance.cols)]
            else:
                self.grid = grid
            self.color = color
            self.gameInstance = gameInstance
            self.moveDepth = 0
            self.totalPositionsEncountered = 1
            self.lastPlayerPassed = False
            self.gameOver = False
            self.validMoves = []
            self.moveHistory = []
            self.sumBlack = 0
            self.sumWhite = 0
            self.sumEmpty = gameInstance.rows * gameInstance.cols

        def getWinner(self):
            if not self.gameOver:
                return -1
            if self.sumBlack > self.sumWhite:
                return 2
            if self.sumBlack < self.sumWhite:
                return 1
            return 0
        
        # probably wont need this?  working with one instance of position that has 
        # moves done and then undone to save copying every move evaluation
        def copy(self):
            newPos = copy.deepcopy(self)
            newPos.gameInstance = self.gameInstance
            return newPos

        # Assumes that if the move is a pass, then it is the only possible move
        # I.e. does not consider whether other moves are possible if it is validating a pass
        def isMoveValid(self, move):
            # If game is over, no move is valid.
            if self.gameOver:
                return False
            # If the color of the move does not match the color of the board, or if it is not [1] or [2] it is invalid
            if self.color != move.color or self.color not in [1, 2]:
                return False
            # If the move is a pass, then it is valid. (see assumption)
            if move.isPassMove():
                return True
            # If the move is out of the board, then it is invalid (except for passes)
            if not self.gameInstance.inBounds(move.row, move.col):
                return False
            # If a move's space is not empty, then it is invalid
            if not self.getCell(move.row, move.col) == 0:
                return False
            # If the move does not flip any tokens, it is invalid
            if not self._getFlippedTokens(move):
                return False
            return True

        # Returns a list of tokens that would be flipped by the given move
        def _getFlippedTokens(self, move):
            flippedTokens = []
            # //TODO optimize so only called once per move
            if move.isPassMove():
                return []
            for rowDelta in [-1, 0, 1]:
                for colDelta in [-1, 0, 1]:
                    # Don't consider the occupied cell
                    if (rowDelta == 0 and colDelta == 0): 
                        continue

                    i = rowDelta
                    j = colDelta

                    flippableTokens = []

                    # Check to see if the direction has opposite-colored tokens adjacent
                    # If so, add the indices of each token until it hits an empty space, a same-colored token, or the border
                    while (
                        self.gameInstance.inBounds(move.row + i, move.col + j) and
                        self.getCell(move.row + i, move.col + j) == Pythello.inverseColor[move.color]
                    ):
                        flippableTokens.append([move.row + i, move.col + j])
                        i += rowDelta
                        j += colDelta
                    
                    # Check to see if the direction ends in a same-colored token
                    # If so, add all opposite-colored tokens encountered to list of flipped tokens
                    # Otherwise, no tokens are flipped
                    if (self.gameInstance.inBounds(move.row + i, move.col + j) and
                        self.getCell(move.row + i, move.col + j) == move.color
                    ):
                        flippedTokens = flippedTokens + flippableTokens
            return flippedTokens


        def doMove(self, move):
            #for moves in self.validMoves:
            #    moves.print()
            # Check move is valid
            if not self.isMoveValid(move):
                return False

            # If the move is a pass
            if move.isPassMove():
                # check for the end of the game (both players have passed)
                if (self.lastPlayerPassed):
                    self.gameOver = True
                else:
                    # Otherwise, mark last player passed
                    self.lastPlayerPassed = True
            else:
                # If the move is not a pass, it is a placement of a token
                self.lastPlayerPassed = False
                # Set new color of square to move's color
                self.setCell(move.row, move.col, move.color)

                # List of tokens flipped by this move
                flippedTokens = self._getFlippedTokens(move)

                # Set all flipped tokens to the new color
                for row_col in flippedTokens:
                    self.setCell(row_col[0], row_col[1], move.color)

                # Give the move a list of all the tokens it flipped for use when undoing the move
                move.setFlippedTokens(flippedTokens)

            # Every valid turn, either a placement or a pass, do:
            self.moveDepth += 1
            self.totalPositionsEncountered += 1
            # Flip the color of the next turn
            self.color = Pythello.inverseColor[move.color]
            # Generate list of valid moves for the next turn
            self.validMoves = self.makeMoveList()
            
            #print("Totals:  Black - %d  |  White - %d  |  Empty - %d"%(self.sumBlack, self.sumWhite, self.sumEmpty))

            return True

        # Assumes that the move was valid, and was the most recently performed move.
        def undoMove(self, move):
            # If last move was a pass or a gameover pass, we don't need to change tokens back and just need to update the variables
            if self.gameOver:
                self.gameOver = False
            elif self.lastPlayerPassed:
                self.lastPlayerPassed = False
            else:
                # Otherwise, the move was a token placement, so we
                # remove added token and unflip all flipped tokens
                self.setCell(move.row, move.col, 0)
                for row_col in move.flippedTokens:
                    self.setCell(row_col[0],row_col[1],Pythello.inverseColor[move.color])

            # Always change color to opposite color.
            self.color = Pythello.inverseColor[move.color]

            # Also, set the move frontier to what it was before the move was played.
            self.validMoves = move.validMoves

            return True

        def makeMoveList(self):
            moveList = []
            for row in range(self.gameInstance.rows):
                for col in range(self.gameInstance.cols):
                    # Check move validity
                    thisMove = Pythello.Move(row, col, self.color)
                    if (self.isMoveValid(thisMove)):
                        moveList.append(thisMove)
            if not moveList:
                # If no move is valid <=> player passes
                moveList.append(Pythello.Move(-1, -1, self.color))

            # Store moveList in each move for backtracking
            for move in moveList:
                move.setValidMoves = moveList
            
            return moveList

        def evaluation(self):
            # return an evaluation of the current position.  
            # Positive values are good for white, negative values are good for black
            return 0

        def print(self):
            for row in self.grid:
                for cell in row:
                    print(cell, "", end='')
                print("")
            print("\n")

        # Sets up the board with the standard start, of a 2x2 square of alternating colors
        def initializeBoardOthello(self):
            row = (int) (self.gameInstance.rows / 2) - 1
            col = (int) (self.gameInstance.cols / 2) - 1
            self.setCell(row,     col, 2)
            self.setCell(row,   col+1, 1)
            self.setCell(row+1,   col, 1)
            self.setCell(row+1, col+1, 2)
            self.validMoves = self.makeMoveList()

        def setCell(self, row, col, color):
            cell = self.getCell(row, col)
            if color == 0:
                if cell == 1:
                    self.sumBlack -= 1
                    self.sumEmpty += 1
                if cell == 2:
                    self.sumWhite -= 1
                    self.sumEmpty += 1
            if color == 1:
                if cell == 2:
                    self.sumWhite -= 1
                    self.sumBlack += 1
                if cell == 0:
                    self.sumEmpty -= 1
                    self.sumBlack += 1
            if color == 2:
                if cell == 1:
                    self.sumBlack -= 1
                    self.sumWhite += 1
                if cell == 0:
                    self.sumEmpty -= 1
                    self.sumWhite += 1
            self.grid[row][col] = color

        def getCell(self, row, col):
            return self.grid[row][col]


        # Sets up the board with the standard reversi start, empty but players can place on central 4 squares
        # Might require extra logic
        def initializeBoardReversi(self):
            # TODO: this
            return None

    class Move:
        def __init__(self, row, col, color):
            self.row = row
            self.col = col
            self.color = color
            self.flippedTokens = []
            self.validMoves = []

        def passMove(self, color):
            return self.OthelloMove(-1, -1, color)

        def isPassMove(self):
            return self.row == -1 and self.col == -1

        def setFlippedTokens(self, flippedTokens):
            self.flippedTokens = flippedTokens

        def setValidMoves(self, validMoves):
            self.validMoves = validMoves

        def print(self):
            print("[",self.row,", ",self.col," : ",self.color, "]")

    def newPos(self, color = 1, grid = []):
        return self.Position(self, color, grid) 