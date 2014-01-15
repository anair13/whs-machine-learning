from itertools import product
from copy import copy, deepcopy
from chess import *

# uses alphabeta pruning and a minimax search to find the best move
def best_move(position, depth, alpha, beta):
    best_score = -float('INF')
    if not position: # move is invalid
        return -best_score
    moves = generate_moves(position)

    for move in moves:
        print '\n' + '-' * (2 - depth) + move_to_string(move),
        new_position = make_move(deepcopy(position), *move)
        if not new_position:
            continue
        if depth:
            score = -best_move(new_position, depth - 1, -beta, -alpha) # best move opponent can respond with
        else:
            new_position.side = -new_position.side
            score = evaluate_board(new_position) # current score of board
            print score,
        best_score = max(score, best_score)
        alpha = max(best_score, alpha)
        if alpha >= beta: return alpha
    return best_score
    # add quiescence searching

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

class Brain:
    
    def get_move(self, position):
        alpha = -float('INF')
        beta = float('INF')
        moves = generate_moves(deepcopy(position))
        # calculates to a lower depth first to order the moves for the search at a greater depth
        # since better moves are searched first, there is a higher cutoff chance to avoid searching the bad moves
        for depth in [1]: # kind of arbitrary numbers so far
            
            moves.sort(key = lambda move: best_move(make_move(deepcopy(position), *move), depth, alpha, beta))
            
            print("luluulululululululululu\n"*100)
            for m in moves:
                print '\n' + '-' * (1 - depth) + move_to_string(m),
                best_move(make_move(deepcopy(position), *m), depth, alpha, beta)
        
        
        if not make_move(deepcopy(position), *moves[0]):
            if position.side < 0 and position.black_heat_map[position.board.index(-1)] or position.side > 0 and position.white_heat_map[position.board.index(1)]:
                print "Checkmate!"
            else:
                print "Stalemate!"
        
        print(moves[0])
        
        return moves[0]        
