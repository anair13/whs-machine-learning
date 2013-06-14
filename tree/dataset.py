'''This module deals with reading and storing data'''

from attribute import Attribute
from decisiontree import *
import sys, os, os.path
import random

class Dataset:

    def __init__(self, attributes, data):
        self.attributes = attributes
        self.data = data
    
    def __str__(self):
        return "attributes\n" + str(self.attributes) + "\n\ndata\n" + str(self.data)
    
    def tree(self):
        self.root = DecisionNode(self.attributes, self.data)
        self.root.learn()
        return self.root

def fromFile(name, index = -1, data_in = ".data", names_in = ".names", class_name = "class"):
    '''Assumes data is file_name.data
    Attributes from file_name.names
    Index is the index of the class attribute
    '''
    file_data = name + data_in
    file_names = name + names_in
            
    # parse .data file for data    
    text = open(os.path.dirname(__file__) + '/../data/' + file_data, 'r').read().split('\n')
    data = [[value.strip() for value in line.split(',')] for line in text if line]
    
    # parse .names file for attributes
    names = open(os.path.dirname(__file__) + '/../data/' + file_names, 'r').read().split('\n')
    lines = [line for line in names if line and line[0] != "|" ] # filter
    
    class_att = Attribute(class_name, [s.strip() for s in lines.pop(0).split(',')])
    
    attributes = []
    
    for line in lines:
        n = line.index(":")
        att_name = line[:n]    
        att = Attribute(att_name, [s.strip(' .') for s in line[n+1:].split(',')])
        attributes.append(att)
        
    attributes.append(class_att)
    
    col_data = list(zip(*data))
    col_data[-1], col_data[index] = col_data[index], col_data[-1]
    data = list(zip(*col_data))
    
    return Dataset(attributes, data)
         
def discretize(name, values, data):
    '''Takes the name, list of discrete values, and column of data for the attribute
    Returns an attribute and data with discrete values
    '''
    for i, number in enumerate(data):
        for value in values:
            # compares number to upper bound of range (e.g. 1-10) or single value
            if int(number) <= int(value[value.find('-') + 1:] if '-' in value else value):
                data[i] = value
                break
    return Attribute(name, values), data

def test(dataset, percent_traindata = 50.0, prune = 0):
    '''Test the data by splitting it into testing and training data
    The percent_traindata is approximate, uses math.random
    '''
    traindata = []
    testdata = []
    for record in dataset.data:
        if random.random() < percent_traindata / 100.0:
            traindata.append(record)
        else:
            testdata.append(record)
    
    print("traindata length:", len(traindata))
    print("testdata length:", len(testdata))
    if not (traindata and testdata):
        print("traindata or testdata is empty, make percent closer to 50")
        
    temp_dataset = Dataset(dataset.attributes, traindata)
    temp_r = temp_dataset.tree()
    temp_r.prune(prune)
    
    return temp_r, temp_r.stats(testdata)
