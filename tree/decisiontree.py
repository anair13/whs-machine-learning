'''  This module encapsulates the DecisionTree structure.
It uses the ID3 DecisionTree algorithm and chi-square pruning.
'''

import math
import re
from scipy.stats import chi2
from attribute import Attribute

# test data from _?
ATTRIBUTES = [
Attribute("temperature", [0,1,2]), # ["hot","mild","cool"]
Attribute("outlook", [0,1,2]), # ["sunny","overcast","rainy"]
Attribute("humidity", [0,1]), # ["high","normal"]
Attribute("wind", [0,1]), # ["strong","weak"]
Attribute("playtennis", [0,1]), # ["no","yes"]
]
DATA = [
[0,0,0,1,0],
[0,0,0,0,0],
[0,1,0,1,1],
[1,2,0,1,1],
[2,2,1,1,1],
[2,2,1,0,0],
[2,1,1,0,1],
[1,0,0,1,0],
[2,0,1,1,1],
[1,2,1,1,1],
[1,0,1,0,1],
[1,1,0,0,1],
[0,1,1,1,1],
[1,2,0,0,0],
]

'''
# test data from _?
ATTRIBUTES = [
Attribute("outlook", [0,1,2], ["sunny","overcast","rain"]),
Attribute("wind", [0,1], ["strong","weak"]),
Attribute("playgolf", [0,1], ["no","yes"])
]
DATA = [
[2,0,0],
[0,1,1],
[1,1,1],
[2,1,1],
[0,0,1],
[2,0,0],
[1,0,0]
]
'''

def entropy(data, attribute, unknown = "?"):
    '''Calculates and returns entropy for a given data set and attribute
    entropy is calculated with the formula s(entropy) = (-(p+) * log2 (p+)) - ((p-) * log2 (p-))
    where log2 X is log base 2 of x
    p+ is proportion of positive examples in data
    p- is proportion of negative examples in data
    '''
    if not data:
        return 0
    s = 0
    data = [value for value in data if value != unknown]
    for value in attribute.values:
        proportion = 1.0 * data.count(value) / len(data)
        if proportion > 0:
            s = s - proportion * math.log(proportion, 2)
    return s
    
def gain(data, attributes, attribute_index, unknown = "?"):
    '''Calculates and returns information gain given a specific attribute
    data is the data set
    attributes is the set of all attributes in the data
    attribute_index is the number of the attribute for which the gain is being calculated
    
    Data is organized in columns, attribute is integer
    
    gain is calculated with the formula
    gain = (entropy of set A) - sum of (len(set V) / len(set A) * (entropy of set V)) for all V in set A
    where set A is the set of all data given
    set V is the set of data that have the attribute V in set A (ex. "rainy" for attribute "weather")
    '''
    if not data:
        return 0
    attribute = attributes[attribute_index]
    attribute_col = data[attribute_index]
    examples_col = data[-1]
    e = entropy(examples_col, attributes[-1], unknown)
    for value in attribute.values:
        p = attribute_col.count(value) * 1.0 / len(attribute_col)
        v = []
        for datum, example in zip(attribute_col, examples_col):
            if datum == value:
                v.append(example)
        e = e - p * entropy(v, attributes[-1], unknown)
    return e

def transpose(array):
    '''returns array transposed'''
    return list(zip(*array))

def chisquare(observed, expected, threshold = 0.95, freedom = 0):
    '''Performs chi square test with given parameters
    observed is a list of observed values
    expected is a list of expected values
    observed and expected must be same length
    freedom is the degrees of freedom in the variable
    if freedom not provided, it will be set automatically as len - 1
    threshold is probability threshold desired

    return value is a True or False depending on whether or not list is statistically significant
    
    True for split is "by chance" and prune the decision
    False for split is not "by chance" and do not prune the decision
    '''
    if not freedom:
        freedom = len(expected) - 1
    
    chi = 0
    for ob, ex in zip(observed, expected):
        if ex:
            chi += (ob - ex) ** 2 / ex
        else:
            pass # Check what the mathematical convention for 0 is
            # looks like we should do
            # freedom = freedom - 1
    
    pval = 1 - chi2.cdf(chi, freedom)
    return pval < threshold

def nint(f, a, b, k = 1000):
    '''Integrate f(t) with respect to t from t = a to b, using k (integer) steps'''
    s = 1.0 * (b - a) / k # step
    return sum([f(t) * s for t in [a + i * s for i in range(k)]])

class DecisionNode:
    '''A node in a decision tree
    has children, attribute list, an attribute (if root attribute is none), and data
    '''
    
    def __init__(self, attributes, data, unknown = "?"):
        '''Initialize with name of attributes and data in lists by attribute'''
        self.attributes = attributes
        self.row_data = data
        self.col_data = transpose(data)
        self.unknown = unknown
        
        self.children = []
        self.attribute = None
        
        for a in self.attributes:
            for v in a.values:
                if v == self.unknown:
                    a.values.remove(v)
        
    def __str__(self):
        return self.printtree()
        
    def printtree(self, depth=1):
        '''
        Returns a string in the form of a list of all the children and their attributes
        Does pretty printing (children are one '|' farther in)
        '''
        s = str(self.attribute) + "? " + str(self.frequency())
        for i, child in enumerate(self.children):
            if child:
                s = s + ("\n" + "| " * depth) + str(self.attribute.values[i]) + "--"
                s = s + (child.printtree(depth + 1) if child.attribute else str(child.frequency()))
        return s
    
    def frequency(self):
        '''Returns absolute frequency distribution 
        by dependent variable in this node
        '''
        if not self.col_data:
            return {}
        result = self.col_data[-1]
        variable = self.attributes[-1]
        f = {}
        for value in variable.values:
            f[value] = result.count(value) * 1.0
        return f
    
    def relative_frequency(self):
        '''Returns relative frequency distribution 
        by dependent variable in this node
        '''
        if not self.col_data:
            return {}
        result = self.col_data[-1]
        variable = self.attributes[-1]
        f = {}
        for value in variable.values:
            f[value] = result.count(value) * 1.0 / len(self.row_data)
        return f
    
    def choose(self):
        f = self.frequency()
        v = list(f.values())
        k = list(f.keys())
        return k[v.index(max(v))]
    
    def learn(self):
        '''Take data and generates tree'''
        
        if not self.row_data or not self.attributes:
            return None
        
        # finds the attribute with best gain
        best_n = 0
        best_g = 0
        for i in range(len(self.attributes) - 1):
            g = gain(self.col_data, self.attributes, i, self.unknown)
            if g > best_g:
                self.attribute = self.attributes[i]
                best_n = i
                best_g = g
        
        # terminate if entropy does not provide enough gain
        if best_g <= 0:
            return None
        
        new_attributes = self.attributes[:best_n] + self.attributes[best_n+1:]

        #creates children nodes using values of attribute with best gain
        for value in self.attribute.values:
            child_data = []
            for row in self.row_data:
                if row[best_n] == value:
                    child_data.append(row[:best_n] + row[best_n+1:])
            self.children.append(DecisionNode(new_attributes, child_data))
        
        for child in self.children:
            child.learn()
            
    def prune(self, threshold = .95):
        '''Prunes this tree based on chi squared test pruning'''      
        for i, child in enumerate(self.children):
            child.prune(threshold)
            if chisquare(child.frequency().values(), self.frequency().values(), threshold):
                self.children[i] = None
    
    def classify(self, record):
        '''Takes a record and returns the classification according to this tree'''
        if not self.attribute:
            f = self.frequency()
            v = list(f.values())
            k = list(f.keys())
            return k[v.index(max(v))]
        
        n = self.attributes.index(self.attribute)
        if record[n] == self.unknown:
            c = None
        else:
            c = self.children[self.attribute.values.index(record[n])]
        
        if not c or not c.frequency():
            f = self.frequency()
            v = list(f.values())
            k = list(f.keys())
            return k[v.index(max(v))]
        return c.classify(record[:n]+record[n+1:])

    def results(self, data = None):
        '''returns the amount of tp (true-positive), tn, fp, fn in an array'''
        if not data:
            data = self.row_data
        ret = {}
        for value in self.attributes[-1].values:
            r = {"tp":0, "tn":0, "fp":0, "fn":0}
            for record in data:
                classification = self.classify(record)
                positive = classification is value
                negative = not positive
                true = (record[-1] == value and positive) or (record[-1] != value and negative)
                false = not true
                r["tp"] += (true and positive)
                r["tn"] += (true and negative)
                r["fp"] += (false and positive)
                r["fn"] += (false and negative)
            ret[value] = r
        return ret
    
    def precision(self, results = None, data = None):
        '''Calculates and returns the precision of the tree
        precision = (true positives / (true positives + false positives))
        '''
        r = results if results else self.results(data)
        return{c: 1.0 * r[c]['tp']/(r[c]['tp']+r[c]['fp']) if r[c]['tp']+r[c]['fp'] != 0 else 0 for c in r}
    
    def recall(self, results = None, data = None):
        '''Calculates and returns the recall of the tree
        precision = (true positives / (true positives + false negative))
        '''
        r = results if results else self.results(data)
        return{c: 1.0 * r[c]['tp']/(r[c]['tp']+r[c]['fn']) if r[c]['tp']+r[c]['fn'] != 0 else 0 for c in r}
    
    def harmonic_mean(self, precision = None, recall = None, results = None, data = None):
        '''Calculates the harmonic mean based on the formula
        2 * (precision * recall)/(precision + recall)
        '''
        p = precision if precision else precision(results, data)
        r = recall if recall else recall(results, data)
        if len(r) != len(p):
            print("length of recall and precision not the same")
            return -1
        return{c: 2.0 * (p[c] * r[c])/(p[c] + r[c]) if p[c]+r[c] != 0 else 0 for c in p}
    
    def stats(self, data = None):
        '''returns the results, precision, recall, and fmeasure'''
        res = self.results(data)
        pre = self.precision(res)
        rec = self.recall(res)
        har = self.harmonic_mean(pre, rec)
        return res, pre, rec, har
    
if __name__ == '__main__':
    root = DecisionNode(ATTRIBUTES,DATA)
    root.learn()
    print(root)
    print("results: " + str(root.results()))
    print("precision: " + str(root.precision()))
    print("recall: " + str(root.recall()))
    
