#! /usr/bin/env python3

from collections import Counter
with open('inputs/day3.txt') as f:
    raw_input = f.read().split('\n')

# Transpose list
processed =  list(zip(*[list(x) for x in raw_input[:-1]]))

counts = [Counter(x) for x in processed]
evens = [x['0'] == x['1'] for x in counts]
most_common = [list(sorted(x.items(), key = lambda y: -y[1]))[0][0] for x in counts]
gamma = int("".join(most_common), base = 2)
epsilon = gamma ^ 2 ** 12 - 1

answer1 = epsilon * gamma
print(f"Answer 1 = {answer1}")

i = len(raw_input[0]) - 1
n_nums = len(raw_input[:-1])

# Sets of indices
o2 = set(range(n_nums))
co2 = o2.copy()
common = o2.copy()

nums =  [int(num, base = 2) for num in raw_input[:-1]]
answer2 = 1

while i > -1 and (len(o2) or len(co2)):

    common = o2.union(co2)
    # If digit i is 0, then bitwise or with 2^(i -1) changes the number
    ones  = { j for j in common if (nums[j] | (2 **i)) == nums[j]}
    if len(o2):
        if  len(o2_ones := o2.intersection(ones)) >=  len(o2) / 2:
            o2 =  o2_ones
        elif len(o2_ones) < len(o2) / 2:
            o2 = o2.difference(ones)
        if len(o2) == 1:
            answer2 *= nums[o2.pop()]
    if len(co2):
        if len(co2_ones := co2.intersection(ones)) >= len(co2) /2 :
            co2 = co2.difference(ones)
        else:
            co2 = co2_ones
        if len(co2) == 1:
            answer2 *= nums[co2.pop()]
    i -= 1

print(f"Answer 2 = {answer2}")


