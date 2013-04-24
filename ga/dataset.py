'''This module deals with reading and storing data'''

from attribute import Attribute
import sys, os, os.path
from genetic import *

class Dataset:

    def __init__(self, attributes, data):
        self.attributes = attributes
        self.data = data

def fromFile(name, index = -1, data_in = ".data", names_in = ".names", class_name = "class"):
    """
    Assumes data is file_name.data
    Attributes from file_name.names
    Index is the index of the class attribute
    """
    file_data = name + data_in
    file_names = name + names_in
    
    #os.chdir()
        
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
    '''
    Takes the name, list of discrete values, and column of data for the attribute
    Returns an attribute and data with discrete values
    '''
    for i, number in enumerate(data):
        for value in values:
            if int(number) <= int(value[value.find('-')+1:] if '-' in value else value):
                data[i] = value
                break
    return Attribute(name, values), data
