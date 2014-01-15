from chess import *
import random

class Brain:
    def get_move(self, position):
        """Returns a random move it finds"""
        return random.choice(generate_moves(position))
