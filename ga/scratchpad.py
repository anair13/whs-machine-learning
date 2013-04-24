from itertools import *

players = ['Matt', 'Ashvin', 'Donald', 'Will', 'Ning', 'Amelia', 'Saavan', 'Ngawang', 'George', 'Kevin']

scores = {
"George": [3, 3, 2, 3, 3, 3], 
"Ashvin": [2, 2, 3, 2, 2, 2], 
"Saavan": [2, 3, 1, 1, 2, 1],
"Kevin": [1, 2, 2, 3, 3, 2], 
"Ning": [2, 1, 2, 2, 2, 1], 
"Donald": [3, 1, 2, 1, 3, 1],
"Amelia": [3, 2, 3, 2, 3, 3], 
"Matt":[1, 2, 3, 1, 1, 1],
"Will": [3, 1, 1, 3, 1, 1], 
"Ngawang": [1, 1, 1, 1, 1, 1]
}


def scores_table(p_indices):
    keys = [players[i] for i in p_indices]
    return [scores[key] for key in keys]

def fitness(table):
    for person in table:
        if person.count(1) != 3:
            return 0
    for r in zip(*table):
        if r.count(1) != 5:
            return 0
    points = 0
    for person, expected_person in zip(table, scores_table(range(10))):
        print([x*y for x,y in zip(person, expected_person)])
        points = points + sum(x*y for x,y in zip(person, expected_person))
    return points
    

print(scores.keys())
print(scores_table(range(10)))

individual1 = [[1,1,1,0,0,0]] * 5 + [[0,0,0,1,1,1]] * 5
individual2 = [[1,1,1,0,0,0]] * 10
print(individual1) 
print(individual2)

print(fitness(individual1))
print(fitness(individual2))


