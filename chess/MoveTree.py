from itertools import product
from copy import copy, deepcopy

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
    
pieces = {0: 0, 'Q': 2, 'b': -5, 'P': 6, 'k': -1, 'B': 5, 'n': -4, 'q': -2, 'p': -6, 'r': -3, 'R': 3, 'N': 4, 'K': 1}

class Position:
    
    def __init__(self, board, side, white_heat_map, black_heat_map, white_king_castle, white_queen_castle,
            white_en_passant, black_king_castle, black_queen_castle, black_en_passant):
        self.board = board
        self.side = -1 # -1 for white, 1 for black
        self.white_heat_map = white_heat_map # number of times each square is attacked by white
        self.black_heat_map = black_heat_map
        self.white_king_castle = white_king_castle
        self.white_queen_castle = white_queen_castle
        self.white_en_passant = white_en_passant # False if not possible, otherwise a list of the two squares the capturing pawn can be in
        self.black_king_castle = black_king_castle
        self.black_queen_castle = black_queen_castle
        self.black_en_passant = black_en_passant
    

# generates all possible moves for the current state of the board
def generate_moves(position):
    moves = [] # returns each move as a tuple (starting square, destination, special move flag)
    board = position.board
    side = position.side
    opp_heat_map = position.white_heat_map if side > 0 else position.black_heat_map
    for i in range(64):
        x, y = i % 8, i / 8
        piece = board[i]
        if piece * side <= 0:
            continue
        if abs(piece) == 1: # king
            for m, n in product([-1, 0, 1], [-1, 0, 1]):
                new_x = x + m
                new_y = y + n
                new_i = new_x + 8 * new_y
                if (m or n) and in_board(new_x, new_y) and board[new_i] * side <= 0 and not opp_heat_map[new_i]:
                    moves.append((i, new_i, 0))
        if abs(piece) == 4: # knight
            for m, n in [(1,2), (-1, 2), (1,-2), (-1,-2), (2, 1), (-2, 1), (2, -1), (-2, -1)]:
                new_x = x + m
                new_y = y + n
                new_i = new_x + 8 * new_y
                if in_board(new_x, new_y) and board[new_i] * side <= 0:
                    moves.append((i, new_i, 0))
        if abs(piece) == 6: # pawn
            new_y = y + piece / 6
            if piece < 0 and new_y == 5 and not (board[i - 8] or board[i - 16]): # white can advance two
                moves.append((i, i - 16, 4))
            elif piece > 0 and new_y == 2 and not (board[i + 8] or board[i + 16]): # black
                moves.append((i, i + 16, 5))
            for m in [-1, 0, 1]:
                new_x = x + m
                new_i = new_x + 8 * new_y
                if in_board(new_x, new_y) and (not m and not board[new_i] or m and board[new_i] * piece < 0):
                    if piece < 0 and new_y == 0 or piece > 0 and new_y == 7:
                        moves.append((i, new_i, 2))
                    else:
                        moves.append((i, new_i, 0))
        if abs(piece) == 2 or abs(piece) == 3: # queen or rook
            for m, n in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_x = x + m
                new_y = y + n
                new_i = new_x + 8 * new_y
                while in_board(new_x, new_y) and board[new_i] * piece <= 0:
                    moves.append((i, new_i, 0))
                    if board[new_i] * piece < 0:
                        break
                    new_x = new_x + m
                    new_y = new_y + n
                    new_i = new_x + 8 * new_y
        if abs(piece) == 2 or abs(piece) == 5: # queen or bishop
            for m, n in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                new_x = x + m
                new_y = y + n
                new_i = new_x + 8 * new_y
                while in_board(new_x, new_y) and board[new_i] * piece <= 0:
                    moves.append((i, new_i, 0))
                    if board[new_i] * piece < 0:
                        break
                    new_x = new_x + m
                    new_y = new_y + n
                    new_i = new_x + 8 * new_y
                    
    if side == -1:
        if position.white_king_castle and board[61] + board[62] + opp_heat_map[60] + opp_heat_map[61] + opp_heat_map[62] == 0:
            moves.append((60, 62, 1))
        if position.white_queen_castle and board[59] + board[58] + board[57] + opp_heat_map[60] + opp_heat_map[59] + opp_heat_map[58] + opp_heat_map[57] == 0:
            moves.append((60, 58, 1))
        if position.white_en_passant:
            if board[position.white_en_passant[0]] == -6:
                moves.append((position.white_en_passant[0], position.white_en_passant[0] - 7, 3))
            if board[position.white_en_passant[1]] == -6:
                moves.append((position.white_en_passant[1], position.white_en_passant[1] - 9, 3))
    else:
        if position.black_king_castle and board[5] + board[6] + opp_heat_map[4] + opp_heat_map[5] + opp_heat_map[6] == 0:
            moves.append((4, 6, 1))
        if position.black_queen_castle and board[3] + board[2] + board[1] + opp_heat_map[4] + opp_heat_map[3] + opp_heat_map[2] + opp_heat_map[1] == 0:
            moves.append((4, 2, 1))
        if position.black_en_passant:
            if board[position.black_en_passant[0]] == 6:
                moves.append((position.black_en_passant[0], position.black_en_passant[0] + 9, 3))
            if board[position.black_en_passant[1]] == 6:
                moves.append((position.black_en_passant[1], position.black_en_passant[1] + 7, 3))
                
    return moves
                    
def generate_heat_map(position):
    board = position.board
    side = position.side
    heat_map = [0] * 64 # keeps track of how many times each square is attacked
    for i in range(64):
        x, y = i % 8, i / 8
        piece = board[i]
        if piece * side <= 0:
            continue
        if abs(piece) == 1: # king
            for m, n in product([-1, 0, 1], [-1, 0, 1]):
                new_x = x + m
                new_y = y + n
                new_i = new_x + 8 * new_y
                if (m or n) and in_board(new_x, new_y):
                    heat_map[new_i] += 1
        if abs(piece) == 4: # knight
            for m, n in [(1, 2), (-1, 2), (1, -2), (-1, -2), (2, 1), (-2, 1), (2, -1), (-2, -1)]:
                new_x = x + m
                new_y = y + n
                new_i = new_x + 8 * new_y
                if in_board(new_x, new_y):
                    heat_map[new_i] += 1
        if abs(piece) == 6: # pawn
            new_y = y + piece / 6
            for m in [-1, 1]:
                new_x = x + m
                if new_x >= 0 and new_x <= 7:
                    new_i = new_x + 8 * new_y
                    heat_map[new_i] += 1
        if abs(piece) == 2 or abs(piece) == 3: # queen or rook
            for m, n in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_x = x + m
                new_y = y + n
                new_i = new_x + 8 * new_y
                while in_board(new_x, new_y):
                    heat_map[new_i] += 1
                    if board[new_i] * piece != 0:
                        break
                    new_x = new_x + m
                    new_y = new_y + n
                    new_i = new_x + 8 * new_y
        if abs(piece) == 2 or abs(piece) == 5: # queen or bishop
            for m, n in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                new_x = x + m
                new_y = y + n
                new_i = new_x + 8 * new_y
                while in_board(new_x, new_y):
                    heat_map[new_i] += 1
                    if board[new_i] * side != 0:
                        break
                    new_x = new_x + m
                    new_y = new_y + n
                    new_i = new_x + 8 * new_y
    return heat_map

def update_heat_map(position, old, start, end, flag):
    def update_piece(piece, board, i, o, heat_map):
        x, y = i % 8, i / 8
        if abs(piece) == 1: # king
            for m, n in product([-1, 0, 1], [-1, 0, 1]):
                new_x = x + m
                new_y = y + n
                new_i = new_x + 8 * new_y
                if (m or n) and in_board(new_x, new_y):
                    heat_map[new_i] += o
        if abs(piece) == 4: # knight
            for m, n in [(1, 2), (-1, 2), (1, -2), (-1, -2), (2, 1), (-2, 1), (2, -1), (-2, -1)]:
                new_x = x + m
                new_y = y + n
                new_i = new_x + 8 * new_y
                if in_board(new_x, new_y):
                    heat_map[new_i] += o
        if abs(piece) == 6: # pawn
            new_y = y + piece / 6
            for m in [-1, 1]:
                new_x = x + m
                if new_x >= 0 and new_x <= 7:
                    new_i = new_x + 8 * new_y
                    heat_map[new_i] += o
        if abs(piece) == 2 or abs(piece) == 3: # queen or rook
            for m, n in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_x = x + m
                new_y = y + n
                new_i = new_x + 8 * new_y
                while in_board(new_x, new_y):
                    heat_map[new_i] += o
                    if board[new_i]:
                        break
                    new_x = new_x + m
                    new_y = new_y + n
                    new_i = new_x + 8 * new_y
        if abs(piece) == 2 or abs(piece) == 5: # queen or bishop
            for m, n in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                new_x = x + m
                new_y = y + n
                new_i = new_x + 8 * new_y
                while in_board(new_x, new_y):
                    heat_map[new_i] += o
                    if board[new_i]:
                        break
                    new_x = new_x + m
                    new_y = new_y + n
                    new_i = new_x + 8 * new_y
                    
    board = position.board
    side = position.side
    piece = board[end]
    if position.side < 0:
        heat_map = position.white_heat_map
        opp_heat_map = position.black_heat_map
    else:
        heat_map = position.black_heat_map
        opp_heat_map = position.white_heat_map
    if flag == 1: # castle
        if end - start == 2: # 0-0
            x, y = start % 8, start / 8
            for m, n in [(-1, 0), (-1, side), (0, side)]: # each of the squares that does not overlap with the king's new position
                new_i = (x + m) + 8 * (y + n)
                heat_map[new_i] -= 1
            x, y = end % 8, end / 8
            for m, n in [(1, 0), (1, side), (0, side)]: # each of the squares that does not overlap with the king's old position
                new_i = (x + m) + 8 * (y + n)
                heat_map[new_i] += 1
            x, y, n = (end + 1) % 8, (end + 1) / 8, side
            new_y = y + n
            new_i = x + 8 * new_y
            while in_board(x, new_y): # only checks the ray that goes up from the rook, since it is in a corner
                heat_map[new_i] -= 1
                if board[new_i]:
                    break
                new_y = new_y + n
                new_i = x + 8 * new_y
            heat_map[start] -= 1 # the king's old square, which the rook no longer covers from its old position
            heat_map[start + 1] -= 1 # the square next to the king, which the rook also no longer covers
            x, y = (start + 1) % 8, (start + 1) / 8
            for m, n in [(-1, 0), (0, side)]: # only checks left and up from the rook
                new_x = x + m
                new_y = y + n
                new_i = new_x + 8 * new_y
                while in_board(new_x, new_y):
                    heat_map[new_i] += 1
                    if board[new_i]:
                        break
                    new_x = new_x + m
                    new_y = new_y + n
                    new_i = new_x + 8 * new_y
        else: # 0-0-0
            x, y = start % 8, start / 8
            for m, n in [(1, 0), (1, side), (0, side)]: # each of the squares that does not overlap with the king's new position
                new_i = (x + m) + 8 * (y + n)
                heat_map[new_i] -= 1
            x, y = end % 8, end / 8
            for m, n in [(-1, 0), (-1, side), (0, side)]: # each of the squares that does not overlap with the king's old position
                new_i = (x + m) + 8 * (y + n)
                heat_map[new_i] += 1
            x, y, n = (end - 2) % 8, (end - 2) / 8, side
            new_y = y + n
            new_i = x + 8 * new_y
            while in_board(x, new_y): # only checks the ray that goes up from the rook, since it is in a corner
                heat_map[new_i] -= 1
                if board[new_i]:
                    break
                new_y = new_y + n
                new_i = x + 8 * new_y
            heat_map[start] -= 1 # the king's old square, which the rook no longer covers from its old position
            heat_map[start - 1] -= 1 # the square next to the king, which the rook also no longer covers
            heat_map[start - 3] -= 1 # another square. hardcoding ftw.
            x, y = (start - 1) % 8, (start - 1) / 8
            for m, n in [(1, 0), (0, side)]: # only checks right and up from the rook
                new_x = x + m
                new_y = y + n
                new_i = new_x + 8 * new_y
                while in_board(new_x, new_y):
                    heat_map[new_i] += 1
                    if board[new_i]:
                        break
                    new_x = new_x + m
                    new_y = new_y + n
                    new_i = new_x + 8 * new_y
    else:
        board[start], board[end] = piece, old # temporarily undoes move to do piece's old position
        for i, o in ([(start, -1), (end, 1)] if flag != 3 else [(start, -1), (end, 1), (end - 8 * piece / 6, -1)]):
            if i == start or i == end:
                update_piece(piece, board, i, o, heat_map) # updates the start and end squares for the piece being moved
            else: # en passant case
                update_piece(-piece, board, i, o, opp_heat_map)
            x, y = i % 8, i / 8
            if i == end and old:
                update_piece(old, board, end, -1, opp_heat_map) # removes the heat map squares of the captured piece
                break
            for m, n in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]: # checks if any rooks, bishops, or queens are blocked/unblocked by the move
                new_x = x + m
                new_y = y + n
                new_i = new_x + 8 * new_y
                while in_board(new_x, new_y):
                    if board[new_i] == 2 * side or board[new_i] == 3 * side and abs(m - n) == 1 or board[new_i] == 5 * side and abs(m - n) != 1:
                        rev_x = x - m
                        rev_y = y - n
                        rev_i = rev_x + 8 * rev_y
                        while in_board(rev_x, rev_y):
                            heat_map[rev_i] -= o
                            if board[rev_i]:
                                break
                            rev_x = rev_x - m
                            rev_y = rev_y - n
                            rev_i = rev_x + 8 * rev_y
                        break
                    elif board[new_i] == -2 * side or board[new_i] == -3 * side and abs(m - n) == 1 or board[new_i] == -5 * side and abs(m - n) != 1:
                        rev_x = x - m
                        rev_y = y - n
                        rev_i = rev_x + 8 * rev_y
                        while in_board(rev_x, rev_y):
                            opp_heat_map[rev_i] -= o
                            if board[rev_i]:
                                break
                            rev_x = rev_x - m
                            rev_y = rev_y - n
                            rev_i = rev_x + 8 * rev_y
                        break
                    elif board[new_i]:
                        break
                    new_x = new_x + m
                    new_y = new_y + n
                    new_i = new_x + 8 * new_y
            if i == start:
                if flag == 2: # pawn promotion
                    piece /= 3
                board[start], board[end] = 0, piece
                            
def in_board(x, y):
    return x >= 0 and x <= 7 and y >= 0 and y <= 7

# returns False if the move is invalid, otherwise the updated position
def make_move(position, start, end, flag):
    position.white_en_passant = False
    position.black_en_passant = False
    board = position.board
    old = board[end] # the captured piece that was on the square, if there was one
    if flag == 1: # castle
        if end - start == 2: # king's side
            board[start], board[start + 1], board[end], board[end + 1] = 0, board[end + 1], board[start], 0
        else: # queen's side
            board[start], board[start - 1], board[end], board[end - 2] = 0, board[end - 2], board[start], 0
        if position.side < 0:
            position.white_king_castle = False
            position.white_queen_castle = False
        else:
            position.black_king_castle = False
            position.black_queen_castle = False
    elif flag == 3: # en passant
        if end - start < 0: # white
            board[start], board[end + 8], board[end] = 0, 0, board[start]
        else: # black
            board[start], board[end - 8], board[end] = 0, 0, board[start]
    else:
        if flag == 4: # white pawn advance two
            x = end % 8
            if x == 0:
                position.black_en_passant = [0, end + 1]
            elif x == 7:
                position.black_en_passant = [end - 1, 0]
            else:
                position.black_en_passant = [end - 1, end + 1]
        elif flag == 5: # black pawn advance two
            x = end % 8
            if x == 0:
                position.white_en_passant = [0, end + 1]
            elif x == 7:
                position.white_en_passant = [end - 1, 0]
            else:
                position.white_en_passant = [end - 1, end + 1]
        if start == 60 or start == 63:
            position.white_king_castle = False
        if start == 60 or start == 56:
            position.white_queen_castle = False
        if start == 4 or start == 7:
            position.black_king_castle = False
        if start == 4 or start == 0:
            position.black_queen_castle = False
        board[start], board[end] = 0, board[start] # if flag == 2: promotion will be handled in update_heat_map
    update_heat_map(position, old, start, end, flag)
    '''original_side = position.side
    position.side = -1
    position.white_heat_map = generate_heat_map(position)
    position.side = 1
    position.black_heat_map = generate_heat_map(position)
    position.side = -original_side'''
    if -1 not in board or 1 not in board or position.side < 0 and position.black_heat_map[board.index(-1)] or position.side > 0 and position.white_heat_map[board.index(1)]:
        return False
    position.side = -position.side
    return position

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

def move_to_string(move):
    start = ["a","b","c","d","e","f","g","h"][move[0]%8] + str(8 - move[0] / 8)
    end = ["a","b","c","d","e","f","g","h"][move[1]%8] + str(8 - move[1] / 8)
    return start + "-" + end

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
