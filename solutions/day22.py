#! /usr/bin/env python3
import re
import bisect

with open("inputs/day22.txt") as f:
    raw_input = f.read().split("\n")[:-1]

processed = []

for line in raw_input:
    line = line.split(",")
    instr = re.search("^(?:on)|(?:off)", line[0]).group(0)
    line[0] = line[0].lstrip(instr + " ")
    processed.append(
        "cubes.turn_"
        + instr
        + "(["
        + ", ".join(f'({dim.split("..")[0][2:]}, {dim.split("..")[1]})' for dim in line)
        + "])"
    )


# answer1 =
# print(f"Answer 1 = {answer1}")

# answer2 =
# print(f"Answer 2 = {answer2}")

"""Find containing interval of sorted list"""


def find_interval(l, x):
    if x > max(l):
        return len(l)
    for i in range(len(l)):
        if x < l[i]:
            yield i

class IntervalList():

    def __init__(self):
        self.intervals = []

    def find_interval(self, other):
        if min(other) > max(self.intervals[-1]):
            return len(self.intervals)
        for i in range(len(self.intervals)):
            if max(other) <= self.intervals[i][0]:
                yield i

    """Combine overlapping intervals into single interval"""
    def compact(self):
        i = 0
        while i < len(self.intervals):
            if self.intervals[i][1] == self.intervals[i+1][0]:
                self.intervals[i] = [self.intervals[i][0], self.intervals[i+1][1]]
            else:
                i += 1
        return self

    def add(self, interval):
        which = next(self.find_interval(interval))
        #Case 1: between intervals
        if (which == len(interval) or self.intervals[which][0] >= interval[1]) and (which == 0 or interval[which-1][1] < interval[0]):
            self.intervals.insert(which, interval)
        #Case2: entirely in interval
        elif which > 0 and min(interval) >= min(self.intervals[which -1]) and max(interval) <= max(self.intervals[which -1]):
            pass
        elif





    def __repr__(self):
        return self.intervals.__repr__()

class CubeRange:
    def __init__(self):
        self.on = [IntervalList(), IntervalList(), IntervalList()] 

    def turn_on(self, instr):
        for i, rnge in enumerate(instr):
            if self.on[i] is None:
                self.on[i] = rnge
            else:
                min_i = next(find_interval(self.on[i], rnge[0]))
                max_i = next(find_interval(self.on[i], rnge[1]))

            # If less than min/ greater than max, concatenate
                if max_i == 0:
                    if self.on[i][0] - rnge[1] > 1:
                        self.on = rnge + self.on
                    else:
                        self.on[i][0][0] = rnge[0]
                else:


                elif rnge[1] < min(self.on[i]):
                    self.on[i] = rnge + self.on[i]
                elif rnge[0] > max(self.on[i]]):
                    self.on[i] += rnge

    def turn_off(self, instr):
        for i, rnge in enumerate(instr):
            if self.on[i] is not None:
                if rnge[0] > min(self.on[i]) or rnge[1] < max(self.on[i]):
                # Get insertion indices into sorted list
                    min_i = next(find_interval(self.on[i], rnge[0]))
                    max_i = next(find_interval(self.on[i], rnge[1]))
                    self.on[i].insert(min_i, rnge[0])
                    self.on[i].insert(max_i, rnge[0])
                    # Delete values in between
                    if max_i - min_i > 1:
                        del self.on[min_i:max_i]
        print(self.on)
        def count(self):
            pass
