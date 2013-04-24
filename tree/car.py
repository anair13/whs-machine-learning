'''Data set of car conditions and whether a buyer would buy it 
from http://archive.ics.uci.edu/ml/datasets/Car+Evaluation
'''
import dataset
   
car = dataset.fromFile('car')
r = car.tree()
    
if __name__ == '__main__':
    r.prune(.1)
    
    print(r)
    res, pre, rec, har = r.stats()
    print("\nresults: " + str(res))
    print("precision: " + str(pre))
    print("recall: " + str(rec))
    print("harmonic mean " + str(har))
    
    print("\nTESTING:\n")
    r, stats = dataset.test(car, 50, .1)
    
    print(r)
    res, pre, rec, har = stats
    print("\nresults: " + str(res))
    print("precision: " + str(pre))
    print("recall: " + str(rec))
    print("harmonic mean " + str(har))