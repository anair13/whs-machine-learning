from itertools import *
import pickle
import random
import statistics

import sys
sys.path.append("..")
sys.path.append("../ga")

from ha.hungarian import *
from ga.genetic import *
from ga.dataset import *

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
                    res += 'R' + str(j + 1) + ': ' + "%.2f" % table[i][j] + ', '
            res += 'Total: ' + "%.2f" % sum(table[i]) + '\n'
        res += 'Team total: ' + "%.2f" % sum(sum(r) for r in table)
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
    
    def __repr__(self):
        return str(self.scores)
        
def random_combination(iterable, r):
    "Random selection from itertools.combinations(iterable, r)"
    pool = tuple(iterable)
    n = len(pool)
    indices = sorted(random.sample(range(n), r))
    return tuple(pool[i] for i in indices)
    
def read_scores(file_name):
    file = open(file_name).read().split('\n')[1 : -1]
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

def read_all_scores():
    scores = {}
    seniors = []
    juniors = []
    setup = open('data/setup.csv').read().split('\n')
    year = setup[0].split(',')[1][:2]
    for player in setup[3 : -1]:
        player = player.split(',')
        scores[player[0]] = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[]}
        if player[1] == '12':
            seniors.append(player[0])
        elif player[1] == '11':
            juniors.append(player[0])
    monthnames = [None, 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    for month in ['09', '10', '11', '12', '01', '02', '03', '04', '05', '06']:
        try:
            tryout = open('data/' + year + '_' + month + '_' + monthnames[int(month)] + '/tryout.csv').read().split('\n')
        except IOError:
            continue
        for player in tryout[1 : -1]:
            player = player.split(',')
            for round in range(1, 7):
                scores[player[0]][round].append(int(player[round]) if player[round] != 'N' else None)
        for practice in range(8, 0, -1):
            file = open('data/' + year + '_' + month + '_' + monthnames[int(month)] + '/practice' + str(practice) + '.csv').read().split('\n')
            for player in file[1 : -1]:
                player = player.split(',')
                for round in range(1, 7):
                    scores[player[0]][round].append(int(player[round]) if player[round] != 'N' else None)
    return scores, seniors, juniors
    
def read_month_scores(year, month):
    scores = {}
    seniors = []
    juniors = []
    setup = open('data/setup.csv').read().split('\n')
    for player in setup[3 : -1]:
        player = player.split(',')
        scores[player[0]] = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[]}
        if player[1] == '12':
            seniors.append(player[0])
        elif player[1] == '11':
            juniors.append(player[0])
    monthnames = [None, 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    tryout = open('data/' + str(year) + '_' + ('0' + str(month) if month < 10 else str(month)) + '_' + monthnames[month] + '/tryout.csv').read().split('\n')
    for player in tryout[1 : -1]:
        player = player.split(',')
        for round in range(1, 7):
            scores[player[0]][round].append(int(player[round]) if player[round] != 'N' else None)
    for practice in range(8, 0, -1):
        file = open('data/' + str(year) + '_' + ('0' + str(month) if month < 10 else str(month)) + '_' + monthnames[month] + '/practice' + str(practice) + '.csv').read().split('\n')
        for player in file[1 : -1]:
            player = player.split(',')
            for round in range(1, 7):
                scores[player[0]][round].append(int(player[round]) if player[round] != 'N' else None)
    return scores, seniors, juniors
                    
def from_file(file_name):
    return Team(*read_scores(file_name))

def weight(n):
    # return [.7, .3, .1][n]
    return .5 ** (n+1)

def print_scores(scores):
    for player in scores.keys():
        print(player + " " * (10 - len(player)), end = "")
        print(["%.1f" % i for i in scores[player]])

if __name__ == "__main__":
    import time
    s = time.time()
    
    history, seniors, juniors = read_month_scores(12, 12)
    
    scores = {}
    
    for player in history.keys():
        round_scores = []
        for r in sorted(history[player].keys()):
            array = history[player][r]
            weights = [weight(n) for n in range(len(array))]
            e = statistics.minexpval(array, weights, -.43) # 2/3 certain
            round_scores.append(e)
        scores[player] = round_scores
    
    print_scores(scores)
    
    t = Team(scores, seniors, juniors)
    
    t.write_best_teams()
    
    print(time.time() - s)
