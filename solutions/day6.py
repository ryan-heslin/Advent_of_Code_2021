#! /usr/bin/env python3
from collections import Counter, deque

timer = 8
with open('inputs/day6.txt') as f:
    raw_input = f.read().split(',')

processed = [int(x) for x in raw_input]

def grow(last, iterations, timer = 8):
    for _ in range(iterations):
       new = [(timer + 1)] * Counter(last)[0] 
       last += new
       last = [ x- 1 if x != 0 else 6 for x in last]
    return last

def grow_less_stupid_algorithm(init, iterations, cooldown = 6):
    for _ in range(iterations):
        current = init[0]
        init.rotate(-1)
        init[cooldown] += current
    return init

answer1 = len(grow(processed, 80))
print(f"Answer 1 = {answer1}")

counts = list(list(zip(*sorted(Counter(processed).items(), key = lambda kv: kv[0])))[1])
padded = [0] + counts +  ([0] * (timer - max(processed)))
init = deque(padded)

answer2 = grow_less_stupid_algorithm(init, 256)
answer2 = sum(answer2)
print(f"Answer 2 = {answer2}")
