"""Learns to do optical character recognition using artificial neural nets"""

from __future__ import print_function
import pickle
from network import *

def output_to_text(out):
    """Makes neuron output readable"""
    i = out.index(1)
    i = i + (48 if i < 10 else 55 if i < 36 else 61)
    return chr(i)
    
def print_bitstring(out, size = 10):
    for i in range(size):
        for j in range(size):
            print(out[size * i + j], end = "")
        print()
        
def get_char(n, input_string):
    o = n.output(input_string)
    i = o.index(max(o))
    i = i + (48 if i < 10 else 55 if i < 36 else 61)
    return chr(i)

characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

def counting(stats):
    """counts all the true positives, false positives, and false negatives"""
    results = {}
    for char in characters:
        #don't need true negative
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
                
def precision(results = None, stats = None):
    """
    Calculates and returns the precision of the tree
    precision = (true positives / (true positives + false positives))
    """
    r = results if results else counting(stats)
    return {c: 1.0 * r[c]['tp']/(r[c]['tp']+r[c]['fp']) if r[c]['tp']+r[c]['fp'] != 0 else 0 for c in r}
        
def recall(results = None, stats = None):
    """
    Calculates and returns the recall of the tree
    precision = (true positives / (true positives + false negative))
    """
    r = results if results else counting(stats)
    return{c: 1.0 * r[c]['tp']/(r[c]['tp']+r[c]['fn']) if r[c]['tp']+r[c]['fn'] != 0 else 0 for c in r}

def harmonic_mean(precision = None, recall = None, results = None, data = None):
     """
     Calculates the harmonic mean based on the formula
     2 * (precision * recall)/(precision + recall)
     """
     p = precision if precision else precision(results, data)
     r = recall if recall else recall(results, data)
     if len(r) != len(p):
         print("length of recall and precision not the same")
         return -1
     return{c: 2.0 * (p[c] * r[c])/(p[c] + r[c]) if p[c]+r[c] != 0 else 0 for c in p}

def pretty_print(stats):
    """prints out the results in a nice looking way"""
    results = counting(stats)
    p = precision(results)
    r = recall(results)
    hm = harmonic_mean(p, r)
    
    print("\nStats")
    print("char\t", "results")
    for char in characters:
        print(char, "\t", stats[char]) if char in stats.keys() else print(char, "\t", "{}")
    
    print("\nPrecision, Recall, and Harmonic Mean")
    print("char\t", "precision\t", "recall\t\t", "harmonic mean")
    for char in characters:
        print(char, "\t", "{:.4f}\t\t".format(p[char]), "{:.4f}\t\t".format(r[char]), "{:.4f}\t".format(hm[char]))
    
    correct = sum(results[c]["tp"] for c in characters)
    test_cases = sum(results[c]["fp"] for c in characters) + correct
    print("\nSummary")
    print(test_cases, "test cases")
    print(correct, "correct")
    print("{:.4f} ratio correct".format(1.0 * correct / test_cases))

if __name__ == "__main__":
    """trains on the majority of our data, tests on the remainder"""
    training_examples = pickle.load(open('ocr.txt', 'rb'))
    layers = [100, 100, 62]
    
    testing_examples = []
    for i, c in enumerate(training_examples):
        if i % 55 < 10:
            testing_examples.append(c)
            del(training_examples[i])
        
    n = learn(layers, training_examples * 30, cont_output, .5)
    n.save("ocr_save")

    # model built, now test
    tests = []
    stats = {}
    for i in testing_examples:
        t = (output_to_text(i[-62:]), get_char(n, i))
        tests.append(t)
        letter_stat = stats.setdefault(t[0], {})
        letter_stat[t[1]] = letter_stat.setdefault(t[1], 0) + 1
        stats[t[0]] = letter_stat
    pretty_print(stats)
