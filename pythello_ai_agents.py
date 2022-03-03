from math import inf
import random

class RandomAgent:

    def __init__(self):
        random.seed()

    def selectMove(self, position):
        return random.choice(position.validMoves)

class AlphaBetaAgent:

    def __init__(self, depth):
        self.depth = depth

    def selectMove(self, position):
        bestValue = float(-inf)
        bestMove = None
        for move in position.validMoves:
            moveValue = self.alphabeta(position, self.depth, float(-inf), float(inf))
            if moveValue > bestValue:
                bestValue = moveValue
                bestMove = move
        return bestMove

    def evaluation(self, position):
        return position.sumBlack - position.sumWhite

    def alphabeta(self, position, depth, alpha, beta):
        localalpha = alpha
        bestvalue = float(-inf)

        if (position.getWinner() == position.color):
            return float(-inf)

        if (depth == 0):
            return self.evaluation(position)
        
        movesList = position.validMoves

        for move in movesList:
            position.doMove(move)
            value = -self.alphabeta(position, depth-1, -beta, -localalpha)
            position.undoMove(move)
            bestvalue = max(value, bestvalue)
            if bestvalue >= beta:
                break
            if bestvalue > localalpha:
                localalpha = bestvalue
        return bestvalue

        
class MonteCarloAgent:
    def selectMove(position):
        return NotImplemented

    def monteCarlo(position, numIterations, maxDepth):
        return NotImplemented