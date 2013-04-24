from itertools import combinations
from hungarian import *

class Team:

    def __init__(self, scores, seniors = [], juniors = []):
        self.scores = scores
        self.players = scores.keys() # to preserve an ordered list of players
        self.seniors = seniors
        self.juniors = juniors
        
    def best_table(self, ten_players):
        matrix = generate_matrix(self.scores, ten_players)
        return generate_table(matrix, ten_players, hungarian_math_team(matrix))
    
    def best_score(self, ten_players):
        return sum(sum(row) for row in self.best_table(ten_players))
    
    def best_team(self):
        m = 0
        best = [] # list of teams
        for c in combinations(self.players, 10):
            if not self.validate(c):
                continue # this team is not valid
            s = self.best_score(c)
            if s > m:
                print("------------------")
                self.print_team(c)
                m = s
                best = [c]
            elif s == m:
                self.print_team(c)
                best.append(c)
        return best
    
    def validate(self, team):
        num_sen = sum([1 for person in team if person in self.seniors])
        num_jun = sum([1 for person in team if person in self.juniors])
        return num_sen <= 4 and num_jun <= 4
            
        
    def print_team(self, players):
        scores = self.scores
        res = ''
        matrix = generate_matrix(scores, players)
        table = generate_table(matrix, players, hungarian_math_team(matrix))
        l = max(len(p) for p in players) + 1
        for i in range(10):
            res += players[i] + ':' + ' ' * (l - len(players[i]))
            for j in range(len(table[i])):
                if table[i][j]:
                    res += 'Round' + str(j + 1) + ': ' + str(table[i][j]) + ', '
            res += 'Total: ' + str(sum(table[i])) + '\n'
        res += 'Team total: ' + str(sum(sum(row) for row in table))
        print(res)
        
    def frequency(self, best):
        f = {}
        for team in best:
            for person in team:
                f[person] = f.setdefault(person, 0) + 1
        return f


if __name__ == "__main__":
    
    seniors = ["Saavan", "Donald", "George", "Ashvin", "Ning", "Kevin", "Will", "Brian Fratto"]
    juniors = ["Vibha", "Amelia", "Sharon", "Erica", "Lucy", "Abhilasha", "Richard", "Neil"]
    
    scores = {
        'Alex': [6, 6, 4, 6, 0, 6],
        'Vibha': [6, 6, 6, 4, 6, 6],
        'Saavan': [4, 6, 6, 6, 6, 4],
        'Sharon': [6, 6, 6, 6, 4, 6],
        'Donald': [6, 6, 6, 6, 6, 4],
        'George': [6, 6, 6, 6, 6, 6],
        'Amelia': [6, 6, 6, 6, 6, 6],
        'Ashvin': [6, 6, 2, 6, 6, 6],
        'Sayak': [6, 6, 6, 6, 0, 6],
        'Richard': [6, 6, 6, 6, 4, 6],
        'Kendall': [4, 4, 6, 6, 0, 6],
        'Edward': [6, 6, 6, 4, 0, 6],
        'Ning': [6, 6, 6, 6, 4, 6],
        'Kevin': [4, 6, 6, 6, 4, 6],
    }
    """
    'Amy': [6, 6, 6, 6, 0, 4],
    'Jefferson': [6, 6, 4, 6, 0, 4],
    'Lucy': [4, 6, 2, 2, 2, 2],
    'Kiara': [0, 6, 2, 0, 0, 4],
        'Alexandra': [2, 4, 4, 4, 0, 4],
        'Rosanna': [6, 4, 4, 6, 0, 4],
        'John': [6, 6, 6, 2, 0, 6],
        'Hubert': [4, 6, 4, 2, 0, 4],
        'Quiyue Liu': [0, 4, 6, 4, 0, 4],
        'Erica': [6, 6, 4, 6, 6, 4],
        'Will': [6, 6, 4, 6, 4, 4],
        'Neil': [4, 6, 6, 6, 4, 4],
        'Abhilasha': [4, 6, 2, 2, 2, 2],
        'Brian Fratto': [2, 6, 4, 4, 2, 4]
"""
    print(len(scores))
    import time
    s = time.time()
    t = Team(scores, seniors, juniors)
    
    best = t.best_team()
    print("team combinations" ,len(best))
    print(t.frequency(best))
    print(time.time() - s)
