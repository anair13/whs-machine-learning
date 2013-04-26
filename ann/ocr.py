"""Learns to do optical character recognition using artificial neural nets"""

import pickle
from network import *

def output_to_text(out):
    """Makes neuron output readable"""
    i = out.index(1)
    i = i + (87 if i > 9 else 48)
    return chr(i)
    

    
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


characters = "abcdefghijklmnopqrstuvwxyz0123456789"
def counting(stats):
    results = {}
    
    for char in characters:
        #don't actually need true negative
        info = {"tp":0, "fp":0, "fn":0}
        results[char] = info

    for char in stats.keys():
        for output in stats[char].keys():
            if output == char:
                results[char]["tp"] += stats[char][output] 
            if output != char:
                results[char]["fn"] += stats[char][output]
                results[output]["fp"] += stats[char][output]
    return results
                
def precision(r):
    """
    Calculates and returns the precision of the tree
    precision = (true positives / (true positives + false positives))
    """
    return{c: 1.0 * r[c]['tp']/(r[c]['tp']+r[c]['fp']) if r[c]['tp']+r[c]['fp'] != 0 else 0 for c in r}
        
def recall(r):
    """
    Calculates and returns the recall of the tree
    precision = (true positives / (true positives + false negative))
    """
    return{c: 1.0 * r[c]['tp']/(r[c]['tp']+r[c]['fn']) if r[c]['tp']+r[c]['fn'] != 0 else 0 for c in r}
    
def pretty_print(stats):
    results = counting(stats)
    p = precision(results)
    r = recall(results)
    
    print("\nStats")
    print("char\t", "results")
    for char in characters:
        print(char, "\t", stats[char]) if char in stats.keys() else print(char, "\t", "{}")
    
    print("\nPrecision and Recall")
    print("char\t", "precision\t", "recall")
    for char in characters:
        print(char, "\t", "{:.4f}\t\t".format(p[char]), "{:.4f}".format(r[char]))
            
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
    pretty_print(stats)
    print(len(tests), "test cases")
    print(sum(e == o for e, o in tests), "correct")
