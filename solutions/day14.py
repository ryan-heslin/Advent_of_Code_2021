#! /usr/bin/env python3

from collections import defaultdict, Counter
import numpy as np
from functools import reduce
from itertools import groupby
with open('inputs/day14.txt') as f:
    raw_input = f.read().split('\n')[:-1]


def default(*args, **kwargs):
    return True

sequence = list(raw_input.pop(0))

mappings = { x.split(' -> ')[0] : lambda l, i, val = x.split(' -> ')[1]: l.insert(i, val)  for x in raw_input[1:] }

def expand(sequence, mappings, iterations = 10):
    for __ in range(iterations):
        i = 0
        while i < len(sequence) - 1:
            pair = ''.join(sequence[i:(i +2)])
            no_insert = mappings.get(pair, default)(sequence, i + 1)
            i += 1 + (not no_insert)
    return sequence

def get_answer(expanded):
    count = Counter(expanded).most_common()
    return count[0][1] - count[-1][1]

expanded = expand(sequence.copy(), mappings)
answer1 = get_answer(expanded)
print(f"Answer 1 = {answer1}")


mat = np.matrix(np.zeros(( len(mappings), len(mappings) ), int))
pair_mappings = {}
raw_input.pop(0)

# Map each pair to the two pairs it forms when expanded
for i, pair in enumerate(raw_input):
    split = pair.split(' -> ')
    pair_mappings[split[0]] = [split[0][0] + split[1][0], split[1][0]+  split[0][1], i]

#Fill matrix with ones to indicate which new pairs are formed on expansion
for i, k in enumerate(pair_mappings):
    rows = [pair_mappings[pair_mappings[k][0]][2], pair_mappings[pair_mappings[k][1]][2]]
    mat[rows[0], [i]] = mat[rows[1], [i]] = 1


mappings = { x.split(' -> ')[0] :x.split(' -> ')[1] for x in raw_input }
init = [''.join(sequence[i:(i+2)]) for i in range(0, len(sequence) - 1)]
init = np.matrix([1 if k in init else 0 for k in pair_mappings.keys()], int ,(1, len(pair_mappings))).transpose()

old = init
l = list(mappings.keys())

count = Counter(sequence)
count.update({k :0 for k in set(mappings.values()) if k not in count.keys()})

for __ in range(40):
    for i, x in enumerate(old):
        # Add letters that would be inserted on each expansion
        count[mappings[l[i]]] += old[i, 0]
    new = np.matmul(mat, old)
    old = new


answer2 = max(count.values()) - min(filter(lambda x: x > 0, count.values()))
print(f"Answer 2 = {answer2}")
