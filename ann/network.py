import pickle
import math
import random

class Network(object):
    """Artificial neural network maps inputs to outputs"""
    
    def __init__(self, connections, layers, o_type):
        self.layers = layers
        self.neurons = [Neuron(o_type) for i in range(sum(layers))]
        self.connections = connections # neurons x neurons array
    
    def __str__(self):
        s = ""
        for n in self.connections:
            for i in n:
                s = s + ("  " if i >= 0 else " ") + "%0.3f" % i
            s = s + '\n'
        return s
        
    def output(self, inputs):
        cur_outputs = []
        for i, n in zip(inputs[:self.layers[0]], self.neurons):
            cur_outputs.append(i)
            n.own_value = i
        for i in range(self.layers[0], len(self.neurons)):
            j = self.neurons[i].output(self.connections[i], cur_outputs)
            cur_outputs.append(j)
        return cur_outputs[-self.layers[-1]:]
    
    def error(self, training_example):
        output = self.output(training_example)
        expected_output = training_example[-self.layers[-1]:]
        # print(training_example, expected_output, output)
        return .5 * sum((float(o) - float(e))**2 for o, e in zip(output, expected_output))
    
    def save(self, name):
        """Pickles neural net into name.txt""" 
        pickle.dump(self, open('saves/' + name + '.txt', 'wb'), protocol = 2)

def load_network(name):
    """Unpickles neural net from name.txt"""
    return pickle.load(open('saves/' + name + '.txt', 'rb'))

class Neuron:
    def __init__(self, output_function):
        self.output_function = output_function
        self.delta = 0
        
    def output(self, *args):
        x = self.output_function(*args)
        self.own_value = x
        self.inputs = args[1]
        return x

def activation(weights, inputs):
    """Spits out sum of weighted inputs"""
    return sum(w * float(i) for w, i in zip(weights, inputs))

def disc_output(weights, inputs, threshold = 1):
    """Threshold-based, returns 0 or 1"""
    return activation(weights, inputs) > threshold

def cont_output(weights, inputs):
    """Sigmoid function for inputs"""
    return 1 / (1 + math.exp(-activation(weights, inputs)))

def learn(layers, training_examples, o_type, learning_rate = .01):
    """Returns a trained Network
    layers = [num_inputs, hidden_layer_1, ... , num_outputs]
    training_examples = [(input1, input2, input3, ..., output1, output2)]
    """

    num_inputs = layers[0]
    num_outputs = layers[-1]
    
    connections = []
    for i in range(sum(layers)):
        c = []
        j = len(layers) - 1
        for l in range(len(layers)):
            if sum(layers[:l]) > i:
                j = l - 1
                break
        for k in range(sum(layers[:j])):
            if k > sum(layers[:j]) - layers[j]:
                c.append(random.random() * 2 - 1)
            else:
                c.append(0)
        for k in range(sum(layers[j:])):
            c.append(0)
        connections.append(c)
    n = Network(connections, layers, cont_output)
    
    random.shuffle(training_examples)
    
    for k, t in zip(range(len(training_examples)), training_examples):
       
        """print("training", t, end = " ")
        print("error before:", n.error(t), end = " ")
        print(k, "outputs", n.output(t))"""
        
        if k % 100 == 0:
            print("learned example", k)

        backwards_propagate(n, t[:num_inputs], t[-num_outputs:], learning_rate)
        
        """print("after:", n.error(t), "trained", k, end = " ")
        print("outputs", n.output(t))
        print(n)"""
        
    return n
    
def backwards_propagate(network, training_example, training_outputs, l_rate = .01):
    """Updates weights of the network by propagating errors from training example"""
    layers = network.layers
    neurons = network.neurons
    
    real_outputs = network.output(training_example)
    for i, n in enumerate(neurons[-layers[-1]:]): # calculate deltas of outputs
        n.delta = training_outputs[i] - real_outputs[i] 
        
    for l in range(len(layers) - 2, 0, -1): # iterate backward, excluding ends
        start = sum(layers[:l])
        for i in range(start, start + layers[l]):
            n = neurons[i]
            n.delta = 0
            for o in range(start + layers[l], start + layers[l] + layers[l+1]):
                n.delta = n.delta + neurons[o].delta * network.connections[o][i]
    
    for l in range(1, len(layers)): # iterate forward, excluding inputs
        start = sum(layers[:l])
        for o in range(start, start + layers[l]):
            n = neurons[o]
            dfde = n.own_value * (1 - n.own_value)
            for i in range(start - layers[l - 1], start):
                adjust = l_rate * n.delta * dfde * neurons[i].own_value
                network.connections[o][i] += adjust
    
    return network

if __name__ == "__main__":
    con = [
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0],
    ]

    n = Network(con, [3, 2, 1], cont_output)
    print(n.output([1,2,3]))
    print(n)
    
    n = backwards_propagate(n, [1,2,3], [0])
    print(n.output([1,2,3]))
    print(n)
