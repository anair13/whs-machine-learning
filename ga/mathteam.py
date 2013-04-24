from itertools import *
from genetic import *
from dataset import *
import pickle
import random

import sys
sys.path.append("..")

from ha.hungarian import *

class Team(Population):

    def __init__(self, scores, seniors = [], juniors = []):
        self.scores = scores
        self.players = scores.keys() # to preserve an ordered list of players
        self.seniors = seniors
        self.juniors = juniors
        
        individuals = [random_combination(self.players, 10) for i in range(1000)]
        attributes = [Attribute("p" + str(i), self.players) for i in range(10)]
        self.dataset = Dataset(attributes, individuals)
        
        Population.__init__(self, self.dataset, self.fitness)
        
        self.memo = {}
        
    def best_table(self, ten_players):
        matrix = generate_matrix(self.scores, ten_players)
        return generate_table(matrix, ten_players, hungarian_math_team(matrix))
   
    def best_score(self, ten_players):
        s = pickle.dumps(ten_players, 1)
        if s in self.memo:
            return self.memo[s]
        if not self.validate(ten_players):
            return 0 # invalid team, should not be selected again
        ret = sum(sum(round) for round in self.best_table(ten_players))
        self.memo[s] = ret
        return ret
    
    def best_teams(self):
        for i in range(1,10):
            print("Determining generation " + str(i) + ":")
            self.generation()
            print(self.print_team(self.fittest()), end = '\n\n')
        fits = {}
        for l in self.population:
            t = self.best_score(l)
            fits[t] = fits.get(t, 0) + 1
        best_s = max(self.memo.values())
        return [pickle.loads(key) for key, value in self.memo.items() if value == best_s]
        
    def validate(self, team):
        num_sen = sum(1 for person in team if person in self.seniors)
        num_jun = sum(1 for person in team if person in self.juniors)
        return num_sen <= 4 and num_jun <= 4 and len(set(team)) == 10
        
    def print_team(self, players):
        scores = self.scores
        res = ''
        matrix = generate_matrix(scores, players)
        table = generate_table(matrix, players, hungarian_math_team(matrix))
        l = max(len(p) for p in self.players) + 1
        for i in range(len(players)):
            res += players[i] + ':' + ' ' * (l - len(players[i]))
            for j in range(len(table[i])):
                if table[i][j]:
                    res += 'R' + str(j + 1) + ': ' + str(table[i][j]) + ', '
            res += 'Total: ' + str(sum(table[i])) + '\n'
        res += 'Team total: ' + str(sum(sum(r) for r in table))
        return res
    
    def write_best_teams(self, write_to = "results.txt"):
        print("people testing: ", len(self.scores))
        results = open(write_to, 'w')    
        for team in self.best_teams():
            results.write(self.print_team(team))
            results.write("\n\n")
        results.close()
        
    def fitness(self, ten_players):
        return self.best_score(ten_players) ** 100
        
    def mutate(self, individual):
        """Switch a random person with someone who is not in the team"""
        rest = set(self.players) - set(individual)
        return random_combination(individual, 9) + random_combination(rest, 1)
    
    def breed(self, parent1, parent2):
        """Take all elements in parents and choose 10 randomly"""
        return random_combination(set(parent1) | set(parent2), 10)
        
def random_combination(iterable, r):
    "Random selection from itertools.combinations(iterable, r)"
    pool = tuple(iterable)
    n = len(pool)
    indices = sorted(random.sample(range(n), r))
    return tuple(pool[i] for i in indices)
    
def read_scores(file_name):
    file = open(file_name).read().split('\n')[1 :]
    scores = {}
    seniors = []
    juniors = []
    for player in file:
        player = player.split(',')
        scores[player[0]] = [int(player[round]) for round in range(1, 7)]
        if player[7] == '12':
            seniors.append(player[0])
        elif player[7] == '11':
            juniors.append(player[0])
    return scores, seniors, juniors
    
def from_file(file_name):
    return Team(*read_scores(file_name))

if __name__ == "__main__":
    import time
    s = time.time()
    t = from_file("mathteam_january.csv")
    
    t.write_best_teams()
    
    print(time.time() - s)
