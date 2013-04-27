from network import *

layers = [2, 2, 2]
connections = [
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [5, 0, 0, 0, 0, 0],
    [0, 5, 0, 0, 0, 0],
    [0, 0, 5, 0, 0, 0],
    [0, 0, 0, 5, 0, 0],
] # note: it seems numbers will not go above ~0.7
'''
connections = [
    [0, 0, 0, 0,],
    [0, 0, 0, 0,],
    [1, 0, 0, 0,],
    [0, 1, 0, 0,],
]
'''
training_examples = [[5, 0, 1, 0.5], [0, 5, 0.5, 1], [5, 5, 1, 1], [-5, 0, 0, 0.5], [0, -5, 0.5, 0], [-5, -5, 0, 0]]

real_n = Network(connections, layers, cont_output)
os = []
for i in training_examples:
    os.append(list(i[:2]) + real_n.output(i))
training_examples = os

print(training_examples)

n = learn(layers, training_examples, cont_output, 1)

tests = []
for i in training_examples:
    tests.append((i[-layers[-2]:], n.output(i)))
print(tests)
print(len(tests), "test cases")
print(sum(list(e) == list(o) for e, o in tests), "correct")
print(n)
