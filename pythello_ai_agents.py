from math import inf
import random
from pythello import BLACK, WHITE, EMPTY, INVERSE_COLOR
from mcts import MCTS, PythelloNode

# Each function returns a positive value if the board is "better" by its estimation
#   for the color that is given as input
class EvaluationFunctions:
    
    def MAJORITY(board, color):
        difference = board.statistics["count_black"] - board.statistics["count_white"] 
        return difference if color == BLACK else -difference
    
    def WEIGHTED_MAJORITY(board, color):
        # Should return the weighted sum of the pieces, based on their board board.
        # Might be tally-able during play, similar to the simple sum.
        difference = board.statistics["count_black_weighted"] - board.statistics["count_white_weighted"]
        return difference if color == BLACK else -difference
    
    def MINIMAL_FRONTIER(board, color):
        # should return the negative of the number of potential moves the opponent has
        # i.e. the agent tries to minimize possible moves of the opponent.
        return NotImplementedError()
    
    def PURE_MONTE_CARLO(num_playouts):
        def func(board, color):
            agent = RandomAgent()
            wins = 0
            losses = 0
            for i in range(num_playouts):
                moveDepth = 0
                while not board.game_over:
                    _move = agent.select_move(board)
                    board.do_move(_move)
                    moveDepth += 1
                
                if board.get_winner() == color:
                    wins += 1
                else: 
                    losses += 1
                
                while moveDepth > 0:
                    board.undo_move()
                    moveDepth -= 1
            
            return float(wins) / (float(losses) + float(wins))
        return func
    
    # ------------------------------------------------------------------------------------------------
    # -        Misere functions, i.e. functions that will probably make the agent lose.              -
    # ------------------------------------------------------------------------------------------------
    def MINORITY():
        return -EvaluationFunctions.MAJORITY
    
    def WEIGHTED_MINORITY():
        return -EvaluationFunctions.WEIGHTED_MAJORITY

class RandomAgent:

    def __init__(self):
        random.seed()

    def select_move(self, board):
        return random.choice(board.valid_moves)
    
    def reset(self):
        return
    
    def __str__(self):
        return "Random Agent"

class AlphaBetaAgent:

    def __init__(self, evaluation_function, depth):
        self.depth = depth
        random.seed()
        self.evaluation = evaluation_function

    def select_move(self, board):
        best_value = float(-inf)
        best_moves = []
        moves = list(board.valid_moves)
        for move in moves:
            board.do_move(move)
            move_value = -self.alphabeta(board, self.depth, float(-inf), float(inf))
            board.undo_move()
            #print(move_value)
            if move_value == best_value:
                best_moves.append(move)
                
            if move_value > best_value:
                best_value = move_value
                best_moves = [move]
                
        return random.choice(best_moves)

    def alphabeta(self, board, depth, alpha, beta):
        local_alpha = alpha
        local_best_value = float(-inf)

        if (board.game_over):
            if (board.get_winner() == board.color):
                return float(-inf)
            elif board.get_winner() == INVERSE_COLOR[board.color]:
                return float(inf)
            else:
                # Not sure what to return here
                return 0
        
            
        if (depth == 0):
            return self.evaluation(board, board.color)

        moves_list = list(board.valid_moves)

        for move in moves_list:
            board.do_move(move)
            value = -self.alphabeta(board, depth-1, -beta, -local_alpha)
            board.undo_move()
            local_best_value = max(value, local_best_value)
            if local_best_value >= beta:
                break
            if local_best_value > local_alpha:
                local_alpha = local_best_value
        return local_best_value
    
    def reset(self):
        return
    
    def __str__(self):
        return "AlphaBeta Agent (Depth: %d)" % self.depth

class GreedyAgent:
    
    def __init__(self, evaluation_function):
        random.seed()
        self.evaluation = evaluation_function
    
    def select_move(self, board):
        best_value = float(-inf)
        best_moves = []
        moves = list(board.valid_moves)
        color = board.color
        for move in moves:
            board.do_move(move)
            move_value = self.evaluation(board, color)
            board.undo_move()

            if move_value == best_value:
                best_moves.append(move)
                
            if move_value > best_value:
                best_value = move_value
                best_moves = [move]
                
        # Returns a random choice of the best moves
        return random.choice(best_moves)  
    
    def reset(self):
        return
    
    def __str__(self):
        return "Greedy Agent"

class PureMonteCarloAgent:
    
    def __init__(self, games_per_node=50):
        self.games_per_node = games_per_node
        random.seed()
        self.random_playouts = EvaluationFunctions.PURE_MONTE_CARLO(games_per_node)
        
    def select_move(self, board):
        best_percentage = 0.0
        best_moves = []
        color = board.color
        for move in board.valid_moves:
            board.do_move(move)
            win_percentage = self.random_playouts(board, color)
            print(win_percentage)
            board.undo_move()
            if win_percentage > best_percentage:
                best_moves = [move]
                best_percentage = win_percentage
            else:
                best_moves.append(move)
        print (str(best_percentage) + "***")
        return random.choice(best_moves)

    def reset(self):
        return
    
    def __str__(self):
        return "Pure MonteCarlo Agent (%d playouts)" % self.games_per_node
    
class MonteCarloTreeSearch:
    
    def __init__(self, rollout_per_move = 50):
        self.rollout_count = rollout_per_move
        self.tree = MCTS()
    
    def select_move(self, board):
        node = PythelloNode(board)
        for _ in range(self.rollout_count):
            self.tree.do_rollout(node)
        best_node = self.tree.choose(node)
        return best_node.board.move_history[-1]
    
    def reset(self):
        self.tree = MCTS()
    
    def __str__(self):
        return "Monte Carlo Tree Search (%d rollouts per move)" % self.rollout_count
    
