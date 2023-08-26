from board import *
from random import Random
import time

class Player():
    def choose_action(self, board):
        raise NotImplementedError


class RandomPlayer(Player):
    def __init__(self, seed=None):
        self.random = Random(seed)

    def print_board(self, board):
        print("--------")
        for y in range(24):
            s = ""
            for x in range(10):
                if (x,y) in board.cells:
                    s += "#"
                else:
                    s += "."
            print(s, y)

    def choose_action(self, board):
        self.print_board(board)
        time.sleep(0)
        if self.random.random() > 0.97:
            # 3% chance we'll discard or drop a bomb
            return self.random.choice([
                Action.Discard,
                Action.Bomb,
            ])
        else:
            # 97% chance we'll make a normal move
            return self.random.choice([
                Direction.Left,
                Direction.Right,
                Direction.Down,
                Rotation.Anticlockwise,
                Rotation.Clockwise,
            ])

class MyPlayer(Player):
    def __init__(self, seed=None):
        self.random = Random(seed)
       
        # #WEIGHTS
        # self.heights_w = -9
        # self.bumpy_w = -6.2
        # self.holes_w = -7
        # self.blockades_w = -5.6
       
        #WEIGHTS
        self.heights_w = 0.21
        self.bumpy_w = -1.5
        self.holes_w = -12
        self.blockades_w = -5.5
   
    def print_board(self, board):
        print("--------")
        for y in range(24):
            s = ""
            for x in range(10):
                if (x,y) in board.cells:
                    s += "#"
                else:
                    s += "."
            print(s, y)
           
    #HEURISTICS
    def heights_agg(self, sandbox):
        heights = [0] * 10
        for i in range(10):
            heights_temp = []
            for j in sandbox.cells:
                if j[0] == i:
                    heights_temp.append(j[1])
                if heights_temp:
                    heights[i] = 24 - min(heights_temp)
        return heights
       
    def bumpy(self, heights):
        bumpy = []
        for i in range(len(heights) - 1):
            temp_1 = heights[i]
            temp_2 = heights[i + 1]
            dif = temp_2 - temp_1
            bumpy.append(abs(dif))
        return sum(bumpy)
       
    
    def holes(self, sandbox):
        holes_count = 0
        top_y = 0
        for x in range(10):
            y_column = []
            for y in range(24):
                if (x,y) in sandbox.cells:
                    y_column.append(y)
            if len(y_column) > 0:
                top_y = min(y_column)
                for z in range(top_y, 24):
                    if z not in y_column:
                        holes_count +=1
        return holes_count

   
    def blockades(self, sandbox):
        blockades_count = 0
        for x in range(10):
            flag = False
            for y in range(23,-1,-1):
                if (x,y) not in sandbox.cells:
                    flag = True
                else:
                    if flag:
                        blockades_count += 1
                        flag = False
        return blockades_count
               
    def score_board_change(self, sandbox2, previous_score):
        current_score = sandbox2.score
        score_change = current_score - previous_score
        return score_change
       
       
    def move_to_target(self, sandbox, tx, tr):
       
        moves_list = []
        try:
            x_block = sandbox.falling.left
        except:
            pass

        try:
            for i in range(tr):
                sandbox.rotate(Rotation.Clockwise)
                moves_list.append(Rotation.Clockwise)
        except:
            pass
       
        try:
            if tx < x_block:
                dif = x_block - tx
                for i in range(dif):
                    sandbox.move(Direction.Left)
                    moves_list.append(Direction.Left)
        except:
            pass
       
        try:
            if tx > x_block:
                dif = tx - x_block
                for i in range(dif):
                    sandbox.move(Direction.Right)
                    moves_list.append(Direction.Right)
        except:
            pass
       
        try:
            sandbox.move(Direction.Drop)
            moves_list.append(Direction.Drop)
        except:
            pass
       
        return moves_list
       
    def score_board(self, sandbox):
        heights = self.heights_agg(sandbox)
        score = (self.heights_w * sum(heights)) + (self.holes_w * self.holes(sandbox)) + (self.bumpy_w * self.bumpy(heights))
        return score
   
    def choose_action(self, board):
        # time.sleep(0)
        moves_list = []
        prev_score = board.score
        for tr in range(4):
            for tx in range(10):
                sandbox = board.clone()
                moves = self.move_to_target(sandbox, tx, tr)
                scores_list2 = []
               
                for tra in range(4):
                    for txa in range(10):   
                        sandbox2 = sandbox.clone()
                        moves_ahead = self.move_to_target(sandbox2, txa, tra)
                        score2 = self.score_board(sandbox2)
                        change = self.score_board_change(sandbox2, prev_score)
                        # score2 += change
                        if change < 1500:
                            score2 -= 50             #penalizing the AI
                        else:
                            score2 += change
                        scores_list2.append(score2)
                       
                score = max(scores_list2)
                moves_list.append([score, moves])
       
        # print(moves_list)
        try:
            for i in moves_list:
                if i[0] == max([j[0] for j in moves_list]):
                    return i[1]
        except:
            pass
           
SelectedPlayer = MyPlayer