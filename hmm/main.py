# import numpy as np
import random
from wiki import *

class HMM:

    def __init__(self, start, transition, emission):
        """Needs to convert these inputs to numpy matrices
        start is denoted pi = {state: P}
        transition is denoted a = {state: {state: P}}
        emission is denoted b = {state: {observation: P}}
        """
        self.start = start
        self.transition = transition
        self.emission = emission
        self.states = list(start.keys())
        self.observations = list(emission[self.states[0]].keys())
        
        # storing them as matrices because... why not?
        # self.start_matrix = np.matrix([start[state] for state in self.states])
        # self.trans_matrix = np.matrix([[transition[s][e] for e in self.states] for s in self.states])
        # self.emiss_matrix = np.matrix([[emission[s][e] for e in self.observations] for s in self.states])
        
    def step(state, i = 1):
        """Steps markov model state by i steps
        State is a 1D vector
        Transition is a 2D array
        """
        return (self.trans_matrix ** i) * state
        
    def generate(self, num_observations):
        """Generates num observations from this model"""
        observations = []
        states = []
        state = pick(self.start)        
        for i in range(num_observations):
            observations.append(pick(self.emission[state]))
            states.append(state)
            state = pick(self.transition[state])
        return observations, states
    
    def print_me(self):
        print("Model:")
        print(self.states)
        print(self.observations)
        # print(self.start_matrix)
        # print(self.trans_matrix)
        # print(self.emiss_matrix)
    
    def __repr__(self):
        "print table of HMM matrices"
        return ""

def pick(m):
    """Pick an element from a map {element: probability}
    Assumes sum(P) = 1
    """
    r = random.random()
    s = 0
    for element, probability in m.items():
        s = s + probability
        if s > r:
            return element
  
def probability_of(observations, hmm):
    """The probability of given sequence of observations given the markov model"""
    return sum(forward(observations, len(observations), hmm, s) for s in hmm.states)
    
def forward(observations, n, hmm, state):
    """The probability given hmm of the first n observations and currently at state
    n is be between 1 and len(observations).
    """
    if n == 1:
        return hmm.start[state] * hmm.emission[state][observations[0]]
    return sum(forward(observations, n - 1, hmm, s) * hmm.transition[s][state] for s in hmm.states) * hmm.emission[state][observations[n-1]]

def backward(observations, n, hmm, state):
    """The probability given hmm and state of the first n observations a
    n is be between 1 and len(observations).
    """
    if n == len(observations):
        return 1
    return sum(backward(observations, n + 1, hmm, s) * hmm.transition[s][state] for s in hmm.states) * hmm.emission[state][observations[n-1]]

def state_is(state, n, observations, hmm):
    """The probability given hmm and observations that the nth state is state"""
    return forward(observations, n, hmm, state) * backward(observations, n, hmm, state) / probability_of(observations, hmm)

def best_current_state(states, n, observations, hmm):
    """Returns probability, best state sequence of length len-n accounting for O and ends in state"""
    state = states[0]
    if n == 1:
        return hmm.start[state] * hmm.emission[state][observations[0]], states
    best_score = 0
    ret_states = None
    for s in hmm.states:
        tmp = best_current_state([s] + states, n - 1, observations, hmm)
        score = tmp[0] * hmm.transition[s][state] * hmm.emission[state][observations[n - 1]]
        if score > best_score:
            best_score = score
            ret_states = tmp[1]
    return best_score, ret_states

def best_state_sequence(observations, hmm):
    """Viterbi algorithm for finding most likely state sequence from observations"""
    best = max(best_current_state([s], len(observations), observations, hmm) for s in hmm.states)
    return best[1], best[0]

def extract_model(supervised_sequences):
    """Returns an hmm object with reasonable parameters from observations
    supervised_sequences = [([observations], [states])]
    """
    # a_ij = count(states[i] -> states[j]) / states[i]
    # b_i(k) = count(states[i] -> observations[k]) / states[i]
    # p_i = count(states[i]) / len(seq)
    states = []
    observations = []
    for seq in supervised_sequences:
        states = states + seq[1]
        observations = observations + seq[0]
    u_states = list(set(states))
    u_observations = list(set(observations))
    
    emission = {}
    state_counts = [states.count(s) for s in u_states]
    for i, s in zip(state_counts, u_states):
        p_s = {}
        for o in u_observations:
            p_s[o] = list(zip(states, observations)).count((s, o)) / i
            emission[s] = p_s
            
    start = {}
    beginning_states = [seq[1][0] for seq in supervised_sequences]
    for s in u_states:
        start[s] = beginning_states.count(s) / len(beginning_states)
    
    first_state = []
    second_state = []      
    transition = {}
    for seq in supervised_sequences:
        if seq:
            first_state = first_state + seq[1][:-1]
            second_state = second_state + seq[1][1:]
    state_counts = [first_state.count(s) for s in u_states]
    for i, s1 in zip(state_counts, u_states):
        p_s = {}
        for s2 in u_states:
            p_s[s2] = list(zip(first_state, second_state)).count((s1, s2)) / i
            transition[s1] = p_s
    
    print(u_states)
    print(u_observations)
    print(emission)
    print(transition)
    print(start)
    
def states_at_time(state_1, state_2, t, observations, hmm):
    """P of state_1 at t and state_2 at t+1 and observations[t+1] is seen"""
    return forward(observations, t, hmm, state_1) * hmm.transition[state_1][state_2] * hmm.emission[state_2][observations[t+1]] * backward(observations, t + 1, hmm, state_2) / probability_of(observations, hmm)

def expected_transitions_from(state, observations, hmm):
    return sum(state_is(state, t + 1, observations, hmm) for t in range(len(observations)))

def expected_transitions_from_to(state_1, state_2, observations, hmm):
    return sum(states_at_time(state_1, state_2, t + 1, observations, hmm) for t in range(len(observations)))

if __name__ == "__main__":
    start_probability = {'Healthy': 0.6, 'Fever': 0.4}
     
    transition_probability = {
       'Healthy' : {'Healthy': 0.7, 'Fever': 0.3},
       'Fever' : {'Healthy': 0.4, 'Fever': 0.6},
    }

    emission_probability = {
       'Healthy' : {'normal': 0.5, 'cold': 0.4, 'dizzy': 0.1},
       'Fever' : {'normal': 0.1, 'cold': 0.3, 'dizzy': 0.6},
    }    
    
    h = HMM(start_probability, transition_probability, emission_probability)
    h.print_me()
    print()
    
    o = h.generate(1000)
    '''
    print("Generated observable sequence ", o[0])
    print("from state sequence ", o[1])
    
    print("with probability ", probability_of(o[0], h))
    print()
    
    b_s = best_state_sequence(o[0], h)
    print("Best state sequence that generated is ", b_s[0], " with p = ", b_s[1])
    print()
    
    print("Wikipedia says ")
    print(viterbi(o[0], states, start_probability, transition_probability, emission_probability))
    '''
    extract_model([o])

