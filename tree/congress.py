'''Data set of 1984 congressional voting record
from http://archive.ics.uci.edu/ml/datasets/Congressional+Voting+Records
'''

import dataset

congress = dataset.fromFile('congress', 0)
r = congress.tree()

if __name__ == '__main__':

    print(r)
    res, pre, rec, har = r.stats()
    print("\nresults: " + str(res))
    print("precision: " + str(pre))
    print("recall: " + str(rec))
    print("harmonic mean " + str(har))
    
    print("\nPRUNED:\n")
    r.prune(0.33)
    
    print(r)
    res, pre, rec, har = r.stats()
    print("\nresults: " + str(res))
    print("precision: " + str(pre))
    print("recall: " + str(rec))
    print("harmonic mean " + str(har))

    print("\nTESTING:\n")
    r, stats = dataset.test(congress, 50)
    
    print(r)
    res, pre, rec, har = stats
    print("\nresults: " + str(res))
    print("precision: " + str(pre))
    print("recall: " + str(rec))
    print("harmonic mean " + str(har))