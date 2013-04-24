from attribute import Attribute
from dataset import Dataset
from genetic import Population

def fitness(i):
    return 50 - i[0] ** 2 - i[1] ** 2

i = [x for x in range(-5, 6)]

attributes = [Attribute("x", i), Attribute("y", i)]

data = [[x, y] for x in i for y in i] * 5

final = Population(Dataset(attributes, data), fitness, 1000)

print(final.population)
final.summary()
