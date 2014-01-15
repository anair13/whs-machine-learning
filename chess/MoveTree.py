from itertools import product
from copy import copy, deepcopy
from chess import *

import sys
import os
import threading
import time

sys.setrecursionlimit(10000)

class MoveNode:
# if we arrive at the same position from different paths, we should use the same MoveNode

    def __init__(self, position, depth, alpha, beta, thread, children = []):
        self.position = position
        self.depth = depth # might be unnecessary?
        self.alpha = alpha
        self.beta = beta
        self.children = children # [[score, move, MoveNode]]
        self.best_score = -float('inf')
        self.best_move = None
        self.thread = thread
        
    def generate(self, depth):
        if self.children and not depth:
            return
        if not depth:
            moves = generate_moves(self.position)
            for move in moves:
                new_position = make_move(deepcopy(self.position), *move)
                if not new_position:
                    continue
                score = evaluate_board(new_position)
                if score > self.best_score:
                    self.best_score = score
                    self.best_move = move
                self.children.append([score, move, MoveNode(new_position, self.depth + 1, self.alpha, self.beta, self.thread)])
        else:
            for child in self.children:
                with self.thread.tree_lock:
                    if not self.thread.player_move:
                        child[2].generate(depth - 1)
                        child[0] = child[2].best_score
                        if child[0] > self.best_score:
                            self.best_score = child[0]
                            self.best_move = child[1]
    
    def best_child(self):
        return max(self.children)
    
    def __deepcopy__(self, memo):
        new = MoveNode(deepcopy(self.position, memo), self.depth, self.alpha, self.beta, self.thread, deepcopy(self.children, memo))
        return new
    
    def print_tree(self, depth):
        for c in self.children:
            if depth < 3:
                print "-" * depth + move_to_string(c[1]) + ' score:' + str(c[0]) + ' side:' + str(c[2].position.side)
                c[2].print_tree(depth + 1)
    
piece_values = [0, 10000, 880, 510, 320, 333, 100, -100, -333, -320, -510, -880, -10000]
# http://en.wikipedia.org/wiki/Chess_piece_relative_value

def evaluate_board(position):
    """Evaluates the score based on material and position (white pawn = -100)"""
    board = position.board
    score = 0
    
    # add up material
    for piece in board:
        score = score + piece_values[piece]
    
    # possible_moves = generate_moves(board, side) # this should only be done once for a board
    
    # center control with pawns
    weight = 50
    for i in [27, 28, 35, 36]:
        score = score + weight * ((board[i] == 6) - (board[i] == -6))
    
    weight = 2 # space
    score = score + weight * (sum(position.black_heat_map) - sum(position.white_heat_map))
    
    # pawn structure
    weight = [0, 0, -50, -100, -150, -250, -400] # penalize double, triple pawns
    for i in range(8):
        white_pawns = 0
        black_pawns = 0
        for j in range(8):
            white_pawns = white_pawns + board[8 * j + i] == 6
            black_pawns = black_pawns + board[8 * j + i] == -6
        score = score + weight[black_pawns] - weight[white_pawns]
        
    weight = -20 # penalty for undeveloped pawns
    score = score + weight * (board[8:16].count(6) - board[48:56].count(-6))
    
    weight = -30 # penalty for undeveloped bishops
    score = score + weight * (board[:8].count(5) - board[56:].count(-5))
    
    weight = -25 # penalty for undeveloped knights
    score = score + weight * (board[:8].count(4) - board[56:].count(-4))
    
    # rook on seventh rank
    weight = [0, 50, 150]
    score = score + weight[board[48:56].count(3)] - weight[board[8:16].count(-3)]
    
    return score * position.side

class GrowTree(threading.Thread):

    tree_lock = threading.RLock()
    depth = 0
    score = 0
    player_move = False
    current_tree = None

    def run(self):
        self.tree = MoveNode(Position([3, 4, 5, 2, 1, 5, 4, 3, 6, 6, 6, 6, 6, 6, 6, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -6, -6, -6, -6, -6, -6, -6, -6, -3, -4, -5, -2, -1, -5, -4, -3], -1,
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 2, 2, 3, 2, 2, 3, 2, 2, 1, 1, 1, 4, 4, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 4, 4, 1, 1, 1, 2, 2, 3, 2, 2, 3, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            True, True, False, True, True, False), 0, 0, 0, self)
        while True: # while game is still going
            time.sleep(0.1) # a little time for UI
            self.tree.generate(self.depth)
            self.tree.print_tree(0)
            with self.tree_lock:
                print "copying position... ",
                self.current_tree = deepcopy(self.tree)
                self.depth = self.depth + 1
                print "done copying"
                self.current_tree.print_tree(0)
            # print "starting to search depth", self.depth,
                
    def get_move(self, move):
        print "getting move... waiting for the ply to finish"
        with self.tree_lock:
            print("obtaining move")
            self.player_move = True
            self.current_tree = [child[2] for child in self.current_tree.children if child[1] == move][0]
            self.depth = self.depth - 1
            self.score, to_move, self.current_tree = self.current_tree.best_child()
            self.depth = self.depth - 1
            self.tree = deepcopy(self.current_tree)
            print("move chosen; score: " + str(self.score))
        return to_move

class Brain:

    def __init__(self):
        
        self.time = 10 # seconds to make each move, isnt used currently
        
        self.thread = GrowTree()
        self.thread.start() # dafuq?
    
    def get_move(self, move):
        return self.thread.get_move(move)
