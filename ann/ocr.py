"""Learns to do optical character recognition using artificial neural nets"""

print("starting")

import pickle
print("imported pickle")

def output_to_text(out):
    """Makes neuron output readable"""
    i = out.index(1)
    i = i + (87 if i > 9 else 48)
    return chr(i)
    
from network import *
    
def print_bitstring(out, size = 10):
    for i in range(size):
        for j in range(size):
            print(out[size * i + j], end = "")
        print()
        
def get_char(n, input_string):
    o = n.output(input_string)
    i = o.index(max(o))
    i = i + (87 if i > 9 else 48)
    return chr(i)

if __name__ == "__main__":
    training_examples = []
    for line in open('ocr.txt', 'r'):
        s = line[:-1]
        l = []
        for i in s:
            l.append(float(i))
        training_examples.append(l)
    layers = [100, 50, 36]

    n = learn(layers, training_examples * 10, cont_output, .5)
    n.save("ocr_save")

    # model built, now test
    tests = []
    stats = {}
    for i in training_examples:
        t = (output_to_text(i[-36:]), get_char(n, i))
        tests.append(t)
        letter_stat = stats.setdefault(t[0], {})
        letter_stat[t[1]] = letter_stat.setdefault(t[1], 0) + 1
        stats[t[0]] = letter_stat
    print(stats)
    print(len(tests), "test cases")
    print(sum(e == o for e, o in tests), "correct")
