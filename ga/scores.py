from attribute import Attribute
from dataset import Dataset
from genetic import Population

attributes = [Attribute("score", list(range(-5,6))),]

data = [
[5],
[4],
[3],
[2],
[1],
[0],
[-1],
[-2],
[-3],
[-4],
[-5],
]

data = data * 10

scores = Population(Dataset(attributes, data), lambda i: 5 - abs(i[0]), rseed=1)

print(scores)
for i in range(100):
    scores.generation()
print(scores)
print(scores.frequency())
