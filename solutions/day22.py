#! /usr/bin/env python3
import re


def compute_volume(instructions, on, part1):
    known = {}
    added = {}
    volume = 0
    for i, line in enumerate(instructions):
        added = {}
        if part1[i]:
            current = eval(line)
            for k, v in known.items():
                new = v.intersection(current)
                if new.volume != 0:
                    index = k + (i,)
                    added[index] = new
                    if (len(index)) % 2 == 0:
                        volume -= new.volume
                    else:
                        volume += new.volume
            # All added keys should be new
            if on[i]:
                added[(i,)] = current
                volume += current.volume  #  Only need single volume if ON cube
            known = {**known, **added}
    return volume


# Overlapping intervals
def overlap(x, y):
    out = [(None, None), (None, None), (None, None)]
    for i in range(3):
        if (
            None in x[i] or None in y[i] or x[i][1] < y[i][0] or x[i][0] > y[i][1]
        ):  # Disjoint
            out[i] = (None, None)
        elif x[i][0] <= y[i][0]:
            if x[i][1] <= y[i][1]:
                out[i] = (y[i][0], x[i][1])  # x[i] goes past left
            else:
                out[i] = y[i]  # y[i] contained in x[i]
        elif x[i][0] >= y[i][0]:
            if x[i][1] <= y[i][1]:
                out[i] = x[i]  # x[i] contained in y[i]
            else:
                out[i] = (x[i][0], y[i][1])  # x[i] goes past right
    return out


class Space:
    def __init__(self, x, y, z):
        self.coords = [x, y, z]
        self.spans = []
        volume = 1
        for pair in self.coords:
            if None in pair:
                self.spans = [(None, None), (None, None), (None, None)]
                volume = 0
                break
            new = pair[1] - pair[0] + 1
            volume *= new
            self.spans.append(new)
        self.volume = volume

    def intersection(self, other):
        if other is None:
            return self  # Reference semantics surprisingly didn't bite me this time
        if self.volume == 0:
            out = __class__((None, None), (None, None), (None, None))
        else:
            new = overlap(self.coords, other.coords)
            out = __class__(*new)
        return out

    def __repr__(self):
        return self.coords.__repr__() + "\nVolume: " + str(self.volume) + "\n"


with open("inputs/day22.txt") as f:
    raw_input = f.read().split("\n")[:-1]

processed = []
on = []
part1 = []

for line in raw_input:
    instr, line = line.split(" ")
    on.append(instr == "on")
    part1.append(max(abs(int(x)) for x in re.findall(r"-?\d+", line)) <= 50)
    line = re.sub(r"(-?\d+)\.{2}(-?\d+)", r"(\1,\2)", line)
    line = f"Space({line})"
    processed.append(line)


answer1 = compute_volume(processed, on, part1=part1)
print(f"Answer 1: {answer1}")

part1 = [True] * len(processed)

answer2 = compute_volume(processed, on, part1=part1)
print(f"Answer 2: {answer2}")


# Need to account for splitting of cubes
# class IntervalList():
#
# def __init__(self, lower, upper):
# self.lowers = [lower]
# self.uppers = [upper]
#
# def __repr__(self) -> str:
# return "\n".join(f"{self.lowers[i]}  {self.uppers[i]}" for i in range(len(self.lowers)))
#
# def coverage(self):
# return sum(upper - lower + 1 for upper, lower in zip(self.lowers, self.uppers))
#
#
# def find_interval(l, x):
# if x > max(l):
# return len(l)
# for i in range(len(l)):
# if x < l[i]:
# yield i
#
# class IntervalList():
#
# def __init__(self):
# self.intervals = []
#
# def find_interval(self, other):
# if min(other) > max(self.intervals[-1]):
# return len(self.intervals)
# for i in range(len(self.intervals)):
# if max(other) <= self.intervals[i][0]:
# yield i
#
# """Combine overlapping intervals into single interval"""
# def compact(self):
# i = 0
# while i < len(self.intervals):
# if self.intervals[i][1] == self.intervals[i+1][0]:
# self.intervals[i] = [self.intervals[i][0], self.intervals[i+1][1]]
# else:
# i += 1
# return self
#
# def add(self, interval):
# which = next(self.find_interval(interval))
##Case 1: between intervals
# if (which == len(interval) or self.intervals[which][0] >= interval[1]) and (which == 0 or interval[which-1][1] < interval[0]):
# self.intervals.insert(which, interval)
##Case2: entirely in interval
# elif which > 0 and min(interval) >= min(self.intervals[which -1]) and max(interval) <= max(self.intervals[which -1]):
# pass
# elif
#
#


# def __repr__(self):
# return self.intervals.__repr__()
#
# class CubeRange:
# def __init__(self):
# self.on = [IntervalList(), IntervalList(), IntervalList()]
#
# def turn_on(self, instr):
# for i, rnge in enumerate(instr):
# if self.on[i] is None:
# self.on[i] = rnge
# else:
# min_i = next(find_interval(self.on[i], rnge[0]))
# max_i = next(find_interval(self.on[i], rnge[1]))
#
## If less than min/ greater than max, concatenate
# if max_i == 0:
# if self.on[i][0] - rnge[1] > 1:
# self.on = rnge + self.on
# else:
# self.on[i][0][0] = rnge[0]
# else:
#
#
# elif rnge[1] < min(self.on[i]):
# self.on[i] = rnge + self.on[i]
# elif rnge[0] > max(self.on[i]]):
# self.on[i] += rnge
#
# def turn_off(self, instr):
# for i, rnge in enumerate(instr):
# if self.on[i] is not None:
# if rnge[0] > min(self.on[i]) or rnge[1] < max(self.on[i]):
## Get insertion indices into sorted list
# min_i = next(find_interval(self.on[i], rnge[0]))
# max_i = next(find_interval(self.on[i], rnge[1]))
# self.on[i].insert(min_i, rnge[0])
# self.on[i].insert(max_i, rnge[0])
## Delete values in between
# if max_i - min_i > 1:
# del self.on[min_i:max_i]
# print(self.on)
# def count(self):
# pass


class Intersections:
    def __init__(self):
        self.mapping = {}

    def __getitem__(self, k, prev=None, depth=0):
        this_i = k[depth]
        val = self.mapping.get(
            this_i,
        )  # unfinished, probably uneccesary
        if val is None:  # New value; create and return
            self.mapping[this_i] = Intersections()
            val = eval(processed[this_i]).intersect(prev)
            self.mapping[this_i] = val

        if depth == len(k) - 1:  # At deepest requested index
            return val  # use prev here?


class Node:
    def __init__(self, val):
        self.val = val
        self.children = {}

    def add_children(self, val):
        pass
