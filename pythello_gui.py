from pythello import Pythello, BLACK, WHITE, EMPTY, INVERSE_COLOR
from graphics import *
from pythello_ai_agents import *
import time


def point_in_bounding_box(point, p_1, p_2):
    return point.getX() >= p_1.getX() and point.getX() < p_2.getX() and point.getY() >= p_1.getY() and point.getY() < p_2.getY()


def init_window(dim_x, dim_y, rows, cols):
    win = GraphWin('ReversAI', dim_x, dim_y, autoflush=False)
    display_grid_black_stones = []
    display_grid_white_stones = []
    display_grid_black_moves = []
    display_grid_white_moves = []
    display_grid_black_last_play = []
    display_grid_white_last_play = []
    display_grid_black_last_flipped = []
    display_grid_white_last_flipped = []
    rows = rows
    cols = cols
    step_x = dim_x / cols
    step_y = dim_y / rows

    for row in range(rows):
        display_grid_black_stones.append([])
        display_grid_white_stones.append([])
        display_grid_black_moves.append([])
        display_grid_white_moves.append([])
        display_grid_black_last_play.append([])
        display_grid_white_last_play.append([])
        display_grid_black_last_flipped.append([])
        display_grid_white_last_flipped.append([])
        
        for col in range(cols):
            square = Rectangle(Point(step_x * col, step_y * row),
                               Point(step_x * (col + 1), step_y * (row + 1)))
            square.setFill("green")
            square.setOutline("darkgreen")
            square.setWidth(5)
            square.draw(win)

            stone_b = Circle(Point(step_x * (col + .5), step_y *
                                  (row + .5)), min(step_x, step_y)/2.3)
            stone_b.setWidth(0)
            stone_b.setFill("black")
            stone_b.drawn = False
            display_grid_black_stones[row].append(stone_b)

            stone_w = Circle(Point(step_x * (col + .5), step_y *
                                  (row + .5)), min(step_x, step_y)/2.3)
            stone_w.setWidth(0)
            stone_w.setFill("white")
            stone_w.drawn = False
            display_grid_white_stones[row].append(stone_w)

            move_b = Circle(Point(step_x * (col + .5), step_y *
                                 (row + .5)), min(step_x, step_y)/4)
            move_b.setOutline("black")
            move_b.setFill("green")
            move_b.setWidth(5)
            move_b.drawn = False
            display_grid_black_moves[row].append(move_b)

            move_w = Circle(Point(step_x * (col + .5), step_y *
                                 (row + .5)), min(step_x, step_y)/4)
            move_w.setOutline("white")
            move_w.setFill("green")
            move_w.setWidth(5)
            move_w.drawn = False
            display_grid_white_moves[row].append(move_w)
            
            prev_b = Circle(Point(step_x * (col + .5), step_y *
                                 (row + .5)), min(step_x, step_y)/8)
            prev_b.setOutline("black")
            prev_b.setFill("white")
            prev_b.setWidth(5)
            prev_b.drawn = False
            display_grid_black_last_play[row].append(prev_b)
            
            prev_w = Circle(Point(step_x * (col + .5), step_y *
                                 (row + .5)), min(step_x, step_y)/8)
            prev_w.setOutline("white")
            prev_w.setFill("black")
            prev_w.setWidth(5)
            prev_w.drawn = False
            display_grid_white_last_play[row].append(prev_w)
            
            prev_f_b = Circle(Point(step_x * (col + .5), step_y *
                                 (row + .5)), min(step_x, step_y)/16)
            prev_f_b.setOutline("black")
            prev_f_b.setFill("white")
            prev_f_b.setWidth(5)
            prev_f_b.drawn = False
            display_grid_black_last_flipped[row].append(prev_f_b)
            
            prev_f_w = Circle(Point(step_x * (col + .5), step_y *
                                 (row + .5)), min(step_x, step_y)/16)
            prev_f_w.setOutline("white")
            prev_f_w.setFill("black")
            prev_f_w.setWidth(5)
            prev_f_w.drawn = False
            display_grid_white_last_flipped[row].append(prev_f_w)
    win.update()
    return {
        "win": win,
        "stones_b": display_grid_black_stones,
        "stones_w": display_grid_white_stones,
        "moves_b": display_grid_black_moves,
        "moves_w": display_grid_white_moves,
        "prev_b": display_grid_black_last_play,
        "prev_w": display_grid_white_last_play,
        "prev_f_b": display_grid_black_last_flipped,
        "prev_f_w": display_grid_white_last_flipped,
    }


def update_window(display_object, board, last_play=[], last_flipped=[], draw_valid_moves=True, draw_previous_move=True):
    grid = board.grid
    win = display_object["win"]
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            mb = display_object["moves_b"][row][col]
            mw = display_object["moves_w"][row][col]
            if mb.drawn:
                mb.undraw()
                mb.drawn = False
            if mw.drawn:
                mw.undraw()
                mw.drawn = False
                
            pb = display_object["prev_b"][row][col]
            pw = display_object["prev_w"][row][col]
            if pb.drawn:
                pb.undraw()
                pb.drawn = False
            if pw.drawn:
                pw.undraw()
                pw.drawn = False
                
            pfb = display_object["prev_f_b"][row][col]
            pfw = display_object["prev_f_w"][row][col]
            if pfb.drawn:
                pfb.undraw()
                pfb.drawn = False
            if pfw.drawn:
                pfw.undraw()
                pfw.drawn = False

            sb = display_object["stones_b"][row][col]
            sw = display_object["stones_w"][row][col]
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
                    
        if (draw_previous_move and last_play and last_play[0] != -1 and last_play[1] != -1):
            if board.color == 1:
                previous_move = display_object["prev_b"][last_play[0]][last_play[1]]
            else :
                previous_move = display_object["prev_w"][last_play[0]][last_play[1]]
            if not previous_move.drawn:
                previous_move.draw(win)
                previous_move.drawn = True
            
            previous_flips = display_object["prev_f_b"] if board.color == 1 else display_object["prev_f_w"]
            for flip in last_flipped:
                previous_flip = previous_flips[flip[0]][flip[1]]
                if not previous_flip.drawn:
                    previous_flip.draw(win)
                    previous_flip.drawn = True

        if (draw_valid_moves):
            moves_array = display_object["moves_b"] if board.color == 1 else display_object["moves_w"]
            for move in board.valid_moves:
                if not move.is_pass_move():
                    indicator = moves_array[move.row][move.col]
                    if not indicator.drawn:
                        indicator.draw(win)
                        indicator.drawn = True
    win.update()


def get_input(display_object, board):
    valid_move_indicators = []
    win = display_object["win"]
    moves_array = display_object["moves_b"] if board.color == 1 else display_object["moves_w"]
    for move in board.valid_moves:
        if not move.is_pass_move():
            indicator = moves_array[move.row][move.col]
            if not indicator.drawn:
                indicator.draw(win)
            valid_move_indicators.append(indicator)
    win.update()

    click = win.getMouse()
    if len(board.valid_moves) == 1:
        if move.is_pass_move():
            return move
    while True:
        for i in range(len(valid_move_indicators)):
            if point_in_bounding_box(click, valid_move_indicators[i].getP1(), valid_move_indicators[i].getP2()):
                for indicator in valid_move_indicators:
                    indicator.undraw()
                    indicator.drawn = False
                win.update()
                return board.valid_moves[i]
        click = win.getMouse()


def main():
    game = Pythello(6, 6)
    moveList = []
    board = game.new_pos()
    board.initialize_board_othello()

    dimX = 1000
    dimY = 1000
    display = init_window(dimX, dimY, game.rows, game.cols)
    
    class HumanAgent:
        def select_move(self, board):
            return get_input(display, board)
        
        def reset(self):
            return
        
        def __str__(self):
            return "Player"
    
    depth = 5
    
    #agent_1 = HumanAgent()
    #agent_1 = RandomAgent()
    #agent_1 = GreedyAgent(EvaluationFunctions.MAJORITY)
    #agent_1 = GreedyAgent(EvaluationFunctions.WEIGHTED_MAJORITY)
    agent_1 = AlphaBetaAgent(EvaluationFunctions.MAJORITY, depth)
    #agent_1 = AlphaBetaAgent(EvaluationFunctions.WEIGHTED_MAJORITY, depth)
    #agent_1 = AlphaBetaAgent(EvaluationFunctions.PURE_MONTE_CARLO(5), depth)
    #agent_1 = PureMonteCarloAgent(100)
    #agent_1 = MonteCarloTreeSearch(10)
    
    #agent_2 = HumanAgent()
    #agent_2 = RandomAgent()
    #agent_2 = GreedyAgent(EvaluationFunctions.MAJORITY)
    #agent_2 = GreedyAgent(EvaluationFunctions.WEIGHTED_MAJORITY)
    #agent_2 = AlphaBetaAgent(EvaluationFunctions.MAJORITY, depth)
    #agent_2 = AlphaBetaAgent(EvaluationFunctions.WEIGHTED_MAJORITY, depth)
    #agent_2 = AlphaBetaAgent(EvaluationFunctions.PURE_MONTE_CARLO(5), depth)
    #agent_2 = PureMonteCarloAgent(100)
    agent_2 = MonteCarloTreeSearch(20)

    update_window(display, board, draw_valid_moves=True, draw_previous_move=False)
    
    # flips back and forth during consecutive games.
    agent_1_color = BLACK
    while True:
        while not board.game_over:
            if (board.color == agent_1_color):
                newMove = agent_1.select_move(board)
            else:
                newMove = agent_2.select_move(board)

            if newMove:
                moveList.append(newMove)
                board.do_move(newMove)
            
            prev_move = []
            flipped = []
            if not newMove.is_pass_move():
                prev_move = [newMove.row, newMove.col]
                flipped = newMove.get_flipped_tokens()
            update_window(display, board, prev_move, flipped)
            #time.sleep(.1)
        win_color = board.get_winner()
        win_color_text = "black" if win_color is BLACK else "white"
        
        if win_color == agent_1_color :
            win_text = "WINNER: Agent 1, " + win_color_text +", " + str(agent_1)
        elif win_color == INVERSE_COLOR[agent_1_color]:
            win_text = "WINNER: Agent 2, " + win_color_text +", " + str(agent_2)
        else:
            win_text = str(agent_1) + " ties with " + str(agent_2)
            
        print(win_text)

        while board.move_history:
            board.undo_move()
            update_window(display, board, draw_valid_moves = False, draw_previous_move=False, )
        update_window(display, board, draw_valid_moves = True, draw_previous_move=False, )
        agent_1_color = INVERSE_COLOR[agent_1_color]
        agent_1.reset()
        agent_2.reset()


if __name__ == "__main__":
    main()
