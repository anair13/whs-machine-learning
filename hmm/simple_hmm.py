from hmm import *

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

training_data = []
for i in range(100):
    training_data.append(h.generate(100))

m = extract_model(training_data)
m.print_me()

observations = h.generate(10)
print("observed:")
print(observations[0])
print(observations[1])
print("predicts:")
print(best_state_sequence(observations[0], m)[0])
