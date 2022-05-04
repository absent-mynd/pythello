from math import inf
import random
from pythello import BLACK, WHITE, EMPTY, INVERSE_COLOR
from mcts import MCTS, PythelloNode
from time import time

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
    
    def shortstr(self):
        return "RANDOM" 

class AlphaBetaAgent:

    def __init__(self, evaluation_function, max_time_s, eval_shortstr):
        self.max_time_s = max_time_s
        self.eval_shortstr = eval_shortstr
        random.seed()
        self.evaluation = evaluation_function

    def select_move(self, board):
        start_time = time()
           
        best_value = float(-inf)
        best_moves = []
        moves = list(board.valid_moves)
        depth = 0
        last_iteration_duration = 0
        last_iteration_start = time()
        while (time() - start_time) + last_iteration_duration < self.max_time_s:
            depth += 1
            best_value = float(-inf)
            best_moves = []
            moves = list(board.valid_moves)
            for move in moves:
                board.do_move(move)
                move_value = -self.alphabeta(board, depth, float(-inf), float(inf))
                board.undo_move()
                #print(move_value)
                if move_value == best_value:
                    best_moves.append(move)
                    
                if move_value > best_value:
                    best_value = move_value
                    best_moves = [move]
            last_iteration_duration = time() - last_iteration_start
            last_iteration_start = time()
            #print("depth %d : %f : %f" % (depth,(time() - start_time), last_iteration_duration))
                    
        #print("Best choice value: %f (searched to %d turns ahead)" % (best_value, depth))
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
        return "AlphaBeta Agent (%d seconds max, %s)" % (self.max_time_s, self.eval_shortstr)
    
    def shortstr(self):
        return "ab_%d_%s" % (3, self.eval_shortstr)

class GreedyAgent:
    
    def __init__(self, evaluation_function, eval_shortstr = ""):
        self.eval_shortstr = eval_shortstr
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
        return "Greedy Agent (%s)" % self.eval_shortstr
    
    def shortstr(self):
        return "GREEDY_" + self.eval_shortstr 

class PureMonteCarloAgent:
    
    def __init__(self, max_time_s=10):
        self.max_time_s = max_time_s
        random.seed()
        
    def random_playout(self, board, color):
        agent = RandomAgent()
        moveDepth = 0
        win = False
        
        while not board.game_over:
            _move = agent.select_move(board)
            board.do_move(_move)
            moveDepth += 1
        
        if board.get_winner() == color:
            win = True
        
        while moveDepth > 0:
            board.undo_move()
            moveDepth -= 1
            
        return win
        
        
    def select_move(self, board):
        start_time = time()
        color = board.color
        
        move_win_counts = [0 for i in range(len(board.valid_moves))]
        playout_iterations = 0
        while time() - start_time < self.max_time_s:
            playout_iterations += 1
            for i in range(len(board.valid_moves)):
                move = board.valid_moves[i]
                board.do_move(move)
                if (self.random_playout(board, color)):
                    move_win_counts[i] += 1
                board.undo_move()
        
        best_percentage = 0.0
        best_moves = []
        for i in range(len(board.valid_moves)):
            win_percentage = move_win_counts[i] / playout_iterations
                
            if win_percentage > best_percentage:
                best_moves = [board.valid_moves[i]]
                best_percentage = win_percentage
            elif win_percentage == best_percentage:
                best_moves.append(board.valid_moves[i])
                
        #print (str(best_percentage) + "*** with " + str(playout_iterations) + " playouts per move")
        return random.choice(best_moves)

    def reset(self):
        return
    
    def __str__(self):
        return "Pure MonteCarlo Agent (%d second(s) max)" % self.max_time_s
    
    def shortstr(self):
        return "PMC_%d" % 3 
    
class MonteCarloTreeSearch:
    
    def __init__(self, max_time_s=10):
        self.max_time_s = max_time_s
        self.tree = MCTS(1.41421)
    
    def select_move(self, board):
        start_time = time()
        node = PythelloNode(board)
        i = 0
        while time() - start_time < self.max_time_s:
            i+= 1
            self.tree.do_rollout(node)
        
        best_node = self.tree.choose(node)
        #print("out of ", i, " rollouts.")
        return best_node.board.move_history[-1]
    
    def reset(self):
        self.tree = MCTS(1.41421)
    
    def __str__(self):
        return "Monte Carlo Tree Search (%d second(s) max)" % (self.max_time_s)

    def shortstr(self):
        return "MCTS_%d" % 3  
    
