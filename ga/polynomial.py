from attribute import Attribute
from dataset import Dataset
from genetic import Population

attributes = [Attribute("score", [x/10 for x in range(-50, 50)]),]

data = [[x/10] for x in range(-50, 50)] * 5

scores = Population(Dataset(attributes, data), lambda i: -i[0]**4 + i[0]**3 + 20*i[0]**2 + i[0]-2)

print("using -x^4+x^3+20x^2+x-2\n")
print("initial",scores)
for i in range(1000):
    scores.generation()
print("final",scores)
print("frequency", scores.frequency())
print("mode",scores.mode())
print("fittest",scores.fittest())
