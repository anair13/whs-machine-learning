def stats(array, weights):
    """Returns (mean, stddev) of array based on weights"""
    s = sum(w for v, w in zip(array,weights) if v != None)
    if not array or not s:
        return 0, 0
    if array.count(None) == len(array) - 1: # only one score
        return [a for a in array if a != None][0], 2 ** .5
    mean = sum(v * w for v, w in zip(array,weights) if v != None) / s
    variance = sum(w * (v - mean)**2 for v, w in zip(array, weights) if v != None) / s
    return mean, variance ** .5

def minexpval(array, weights, fudge = -1):
    """Returns the minimum expected value of the array,
    fudge standard deviations below the mean
    """
    res = stats(array, weights)
    return max(0.01, res[0] + fudge * res[1])

if __name__ == "__main__":
    array = [2, 2, 2, 3]
    weights = [1, 1, 1, 1]
    print(stats(array, weights))

