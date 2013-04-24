'''Test data is to calculate a combination of factors to create the best
"genotype" of an individual'''
    
import math
import re
import dataset
import random
import warnings
from attribute import Attribute
from bisect import bisect_left

class Population:

    def __init__(self, dataset, fitness, run_generations = 0, rseed = 0, BREED = 0.7, MUTATION = 0.1):
        self.dataset = dataset
        self.fitness = fitness
        self.BREED = BREED
        self.MUTATION = MUTATION
        self.population = self.dataset.data
        
        if rseed:
            random.seed(rseed)
        
        for i in range(run_generations):
            self.generation()
            
    def __str__(self):
        return str(self.population)
        
    def frequency(self):
        phenotypes = []
        for ind in self.population:
            if ind not in phenotypes:
                phenotypes.append(ind)
        f = {}
        for phenotype in phenotypes:
            f[str(phenotype)] = self.population.count(phenotype)
        return f
        
    def fittest(self):
        return max(self.population, key=self.fitness)
        
    def mode(self):
        f = self.frequency()
        v = list(f.values())
        k = list(f.keys())
        return k[v.index(max(v))]

    def breed(self, parent1, parent2):
        '''
        Inputs are two parent genotypes (list of attribute values)
        Output is a possible child genotype to replace parents in population
        '''  
        child = [] 
        # randomly selects one parent's value for each attribute and passes it to the child
        for val1, val2 in zip(parent1, parent2):
            child.append(val1 if random.random() < 0.5 else val2)
        return child

    def mutate(self, individual):
        attribute_index = random.randint(0, len(self.dataset.attributes) - 1)
        values = self.dataset.attributes[attribute_index].values
        individual[attribute_index] = values[random.randint(0, len(values) - 1)]
        return self.mutate(individual) if random.random() < self.MUTATION else individual
        
    def swapmutate(self, individual):
        att1 = random.randint(0, len(individual) - 1)
        att2 = random.randint(0, len(individual) - 1)
        individual[att1], individual[att2] = individual[att2], individual[att1]
        return self.swapmutate(individual) if random.random() < self.MUTATION else individual

    def generation(self):
        '''
        Generates another iteration of the given population
        based on fitness, crossover, and mutation criteria
        '''
        
        # generates weights based on fitness of an individual
        weights = []
        total_fitness = 0
        
        for weight in [self.fitness(ind) for ind in self.population]:
            if weight < 0:
                warnings.warn("negative fitness: " + str(weight))
                weight = 0 # ASSUMPTION: negative fitness to 0
            # normalizes the weights on a scale from 0 to total_fitness, so that
            # the weights are the difference between consecutive values in the list
            weights.append(weight + weights[-1] if weights else weight)
            total_fitness = total_fitness + weight

        new_pop = []
        
        for ind in self.population:
            rand = random.random()
            if rand < self.MUTATION:
                # creates part of new population using mutations of random individuals
                new_pop.append(self.mutate(ind))
            elif rand < self.MUTATION + self.BREED:
                # creates part of new population using crossovers based on weights
                rand1 = random.random() * total_fitness
                rand2 = random.random() * total_fitness
                parent1 = self.population[bisect_left(weights, rand1)]
                parent2 = self.population[bisect_left(weights, rand2)]
                new_pop.append(self.breed(parent1, parent2))
            else:
                # fills the rest of the population based on weights of individuals
                rand = random.random() * total_fitness
                new_pop.append(self.population[bisect_left(weights, rand)])

        self.population = new_pop
    
    def summary(self):
        """PRINTS summary statistics for this population"""
        print("freq: " + str(self.frequency()))
        print("mode: " + str(self.mode()))
        print("fit.: " + str(self.fittest()))

if __name__ == '__main__':
    machine = dataset.fromFile('machine')
    
