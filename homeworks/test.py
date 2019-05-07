from functools import reduce

a = [1, 1, 2, 3, 4]

def reduce_fn(a, b):
    if a == b:
        return a
    return b

print(list(map(reduce_fn, a)))