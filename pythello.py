import copy
import time

BLACK = 1

WHITE = 2

EMPTY = 0

INVERSE_COLOR = [EMPTY, WHITE, BLACK]

class Pythello:
    # 1 = black   2 = white
    # Black goes first


    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols

    def in_bounds(self, row, col):
        return row < self.rows and row >= 0 and col < self.cols and col >= 0

    class Board:

        def __init__(self, game_instance, color=BLACK, grid=[]):
            if len(grid) == 0:
                self.grid = [[0 for i in range(game_instance.cols)]
                             for j in range(game_instance.rows)]
            else:
                self.grid = grid
            self.color = color
            self.game_instance = game_instance
            self.prev_player_passed = False
            self.game_over = False
            self.valid_moves = []
            self.move_history = []
            self.statistics = {
                "count_black" : 0,
                "count_black_weighted" : 0,
                "count_white" : 0,
                "count_white_weighted" : 0,
                "count_empty" : game_instance.rows * game_instance.cols,
                "move_depth" : 0,
                "total_positions_encountered" : 1
            }

        def get_winner(self):
            if not self.game_over:
                return -1
            if self.statistics["count_black"] > self.statistics["count_white"]:
                return BLACK
            if self.statistics["count_black"] < self.statistics["count_white"]:
                return WHITE
            return EMPTY

        # probably wont need this?  working with one instance of position that has
        # moves done and then undone to save copying every move evaluation
        def copy(self):
            new_pos = copy.deepcopy(self)
            new_pos.game_instance = self.game_instance
            return new_pos

        # Assumes that if the move is a pass, then it is the only possible move
        # I.e. does not consider whether other moves are possible if it is validating a pass
        def is_move_valid(self, move):
            # If game is over, no move is valid.
            if self.game_over:
                return False
            # If the color of the move does not match the color of the board, or if it is not [1] or [2] it is invalid
            if self.color != move.color or self.color not in [BLACK, WHITE]:
                return False
            # If the move is a pass, then it is valid. (see assumption)
            if move.is_pass_move():
                return True
            # If the move is out of the board, then it is invalid (except for passes)
            if not self.game_instance.in_bounds(move.row, move.col):
                return False
            # If a move's space is not empty, then it is invalid
            if not self.get_cell(move.row, move.col) == 0:
                return False
            # If the move does not flip any tokens, it is invalid
            if not self._compute_flipped_tokens(move):
                return False
            # Move is valid
            return True

        # Returns a list of tokens that would be flipped by the given move
        def _compute_flipped_tokens(self, move):
            # returns [] if the flipped tokens havent been computed yet for this move.
            flipped_tokens = move.get_flipped_tokens()
            
            if flipped_tokens:
                return move.get_flipped_tokens()

            if move.is_pass_move():
                return []

            for row_delta in [-1, 0, 1]:
                for col_delta in [-1, 0, 1]:
                    # Don't consider the occupied cell
                    if (row_delta == 0 and col_delta == 0):
                        continue

                    i = row_delta
                    j = col_delta

                    flippable_tokens = []

                    # Check to see if the direction has opposite-colored tokens adjacent
                    # If so, add the indices of each token until it hits an empty space, a same-colored token, or the border
                    while (
                        self.game_instance.in_bounds(move.row + i, move.col + j) and
                        self.get_cell(move.row + i, move.col + j) == INVERSE_COLOR[move.color]
                    ):
                        flippable_tokens.append([move.row + i, move.col + j])
                        i += row_delta
                        j += col_delta

                    # Check to see if the direction ends in a same-colored token
                    # If so, add all opposite-colored tokens encountered to list of flipped tokens
                    # Otherwise, no tokens are flipped
                    if (self.game_instance.in_bounds(move.row + i, move.col + j) and
                            self.get_cell(move.row + i, move.col + j) == move.color):
                        flipped_tokens = flipped_tokens + flippable_tokens

            move.set_flipped_tokens(flipped_tokens)

            # Sanity check
            for token in flipped_tokens:
                if (token[0] == self.game_instance.rows - 1
                    or token[0] == 0
                ) and (token[1] == self.game_instance.cols - 1
                    or token[1] == 0):
                    print("ERROR - FLIPPED A CORNER TOKEN")
                    time.sleep(10000)

            return flipped_tokens

        def do_move(self, move):
            # for moves in self.validMoves:
            #    moves.print()
            # Check move is valid
            if not self.is_move_valid(move):
                return False

            # If the move is a pass
            if move.is_pass_move():
                # check for the end of the game (both players have passed)
                if (self.prev_player_passed):
                    self.game_over = True
                else:
                    # Otherwise, mark last player passed
                    self.prev_player_passed = True
            else:
                # If the move is not a pass, it is a placement of a token
                self.prev_player_passed = False
                # Set new color of square to move's color
                self.set_cell(move.row, move.col, move.color)

                # List of tokens flipped by this move
                flipped_tokens = self._compute_flipped_tokens(move)
                
                # Sanity check
                if not flipped_tokens:
                    raise ValueError("Invalid move - no tokens flipped!  Something is wrong")

                # Set all flipped tokens to the new color
                for row_col in flipped_tokens:
                    self.set_cell(row_col[0], row_col[1], move.color)

            # Every valid turn, either a placement or a pass, do:
            self.statistics["move_depth"] += 1
            self.statistics["total_positions_encountered"] += 1
            # Flip the color of the next turn
            self.color = INVERSE_COLOR[move.color]
            # Generate list of valid moves for the next turn
            self.valid_moves = self.make_move_list()
            
            self.move_history.append(move)

            #print("Totals:  Black - %d  |  White - %d  |  Empty - %d"%(self.sumBlack, self.sumWhite, self.sumEmpty))

            return True

        # Assumes that the move was valid, and was the most recently performed move.
        def undo_move(self):
            move = self.move_history.pop()
            
            # If last move was a pass or a gameover pass, we don't need to change tokens back and just need to update the variables
            if self.game_over:
                self.game_over = False
            elif move.is_pass_move():
                # In this case, the move was a pass but not a gameover pass, so we set the prev_player_passed flag to false
                self.prev_player_passed = False
            else:
                # Otherwise, the move was a token placement, so we
                # check to see if the preceding move was a pass, to set the flag
                if self.move_history and self.move_history[len(self.move_history)-1].is_pass_move():
                    self.prev_player_passed = True
                    
                # then remove added token and unflip all flipped tokens
                self.set_cell(move.row, move.col, EMPTY)
                
                for row_col in move.get_flipped_tokens():
                    self.set_cell(row_col[0], row_col[1],
                                  INVERSE_COLOR[move.color])

            # Always change color to color of the move being undone
            self.color = move.color

            # Also, always set the valid move frontier to what it was before the move was played.
            self.valid_moves = move.get_valid_moves()

            return True

        def make_move_list(self):
            move_list = []
            if self.game_over:
                return []
            for row in range(self.game_instance.rows):
                for col in range(self.game_instance.cols):
                    # Check move validity
                    thisMove = Pythello.Move(row, col, self.color)
                    if (self.is_move_valid(thisMove)):
                        move_list.append(thisMove)
            if not move_list:
                # If no move is valid <=> player passes
                move_list.append(Pythello.Move(-1, -1, self.color))

            # Store moveList in each move for backtracking
            for move in move_list:
                move.set_valid_moves(move_list)

            return move_list

        def print(self):
            for row in self.grid:
                for cell in row:
                    print(cell, "", end='')
                print("")
            print("\n")

        # Sets up the board with the standard start, of a 2x2 square of alternating colors
        def initialize_board_othello(self):
            row = (int)(self.game_instance.rows / 2) - 1
            col = (int)(self.game_instance.cols / 2) - 1
            self.set_cell(row, col, 2)
            self.set_cell(row, col+1, 1)
            self.set_cell(row+1, col, 1)
            self.set_cell(row+1, col+1, 2)
            self.valid_moves = self.make_move_list()

        def update_counters(self, delta_e, delta_b, delta_w):
            self.statistics["count_empty"] += delta_e
            self.statistics["count_black"] += delta_b
            self.statistics["count_white"] += delta_w
            
        def update_weighted_counters(self, delta_b, delta_w):
            self.statistics["count_black_weighted"] += delta_b
            self.statistics["count_white_weighted"] += delta_w

        def set_cell(self, row, col, color):
            assert row != -1
            assert col != -1
            cell = self.get_cell(row, col)
            if cell == color:
                return
            cell_weight = self.get_cell_weight(row, col)
            # for incrementing counters
            delta_b = 0
            delta_b_weighted = 0
            delta_w = 0
            delta_w_weighted = 0
            delta_e = 0

            if color == EMPTY:
                delta_e = 1
            if color == BLACK:
                delta_b = 1
                delta_b_weighted = cell_weight
            if color == WHITE:
                delta_w = 1
                delta_w_weighted = cell_weight

            if cell == EMPTY:
                delta_e -= 1
            if cell == BLACK:
                delta_b -= 1
                delta_b_weighted -= cell_weight
            if cell == WHITE:
                delta_w -= 1
                delta_w_weighted -= cell_weight

            self.update_counters(delta_e, delta_b, delta_w)
            self.update_weighted_counters(delta_b_weighted, delta_w_weighted)

            self.grid[row][col] = color

        def get_cell(self, row, col):
            return self.grid[row][col]

        # Sets up the board with the standard reversi start, empty but players can place on central 4 squares
        # Might require extra logic

        def initialize_board_reversi(self):
            # TODO: this
            return None
        

        SQUARE_WEIGHTS = [
            [ 4, -3,  2,   2,],   
            [-3, -4,  -1,  -1,],    
            [ 2,  -1,  1,   0,],    
            [ 2,  -1,  0,   1,],    
        ]

        # Works best on an 8x8 board, but functions on other board sizes.
        def get_cell_weight(self, row, col):
            last_row = self.game_instance.rows - 1
            last_col = self.game_instance.cols - 1
            
            lookup_row = min(row, abs(last_row - row), 3)
            lookup_col = min(col, abs(last_col - col), 3)
            
            return self.SQUARE_WEIGHTS[lookup_row][lookup_col]
            

    class Move:
        def __init__(self, row, col, color):
            self.row = row
            self.col = col
            self.color = color
            self.flipped_tokens = []
            self.valid_moves = []

        def pass_move(self, color):
            return self.OthelloMove(-1, -1, color)

        def is_pass_move(self):
            return self.row == -1 and self.col == -1

        def set_flipped_tokens(self, flipped_tokens):
            self.flipped_tokens = flipped_tokens

        def set_valid_moves(self, valid_moves):
            self.valid_moves = valid_moves

        def get_flipped_tokens(self):
            return self.flipped_tokens

        def get_valid_moves(self):
            return list(self.valid_moves)

        def print(self):
            print("[", self.row, ", ", self.col, " : ", self.color, "]")

    def new_pos(self, color=1, grid=[]):
        return self.Board(self, color, grid)
