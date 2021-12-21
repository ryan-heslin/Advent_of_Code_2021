#! /usr/bin/env python3

from collections import ChainMap
with open('tests/day18.txt') as f:
    raw_input = f.read()

processed =[eval(num) for num in raw_input.split('\n')[:-1]]


def add(lhs, rhs):
    concatenated = lhs + rhs
    traverse(concatenated)

def split(num):
    first = num // 2
    return [first, num - first]

def is_pair(el):
    return (isinstance(el, list) and
    isinstance(el[0], int) and
    isinstance(el[1], int))

def explode(pair, lhs = None, rhs = None):
    lhs = -pair[0] if not lhs else lhs
    rhs = -pair[1] if not rhs else rhs
    pair[0] += lhs 
    pair[1] == rhs
    return pair

def print_tree(l, depth = 0):
    for el in l:
        if isinstance(el, list):
            print_tree(el, depth + 1)
        else:
            print((" " * depth * 2) + str(el))

def traverse(number, depth = 1):
    pass



#answer1 =
#print(f"Answer 1 = {answer1}")

#answer2 =
#print(f"Answer 2 = {answer2}")

class SnailNumber():

    def __init__(self, l):
        depth = 0 
        cur = l.pop(0)
        while not isinstance(cur, int):
            cur = cur.pop(0)
            depth += 1
        self.head = Node(cur, depth)

        while l:
            cur = l.pop(0)



    def extend(self, other):
        cur = self.head
        other_head = other.head
        # Increase depth of each element by 1 before joining
        while other_head is not None:
            other_head.depth += 1
            other_head = other_head.next
        other_head.depth += 1
        while cur.next is not None:
            cur.depth += 1
            cur = cur.next
        cur.depth += 1
        cur.next = other.head

class Node():
    def __init__(self, val, depth, next = None):
        self.val = val 
        self.depth = depth 
        self.next = next
    def join(self, other):
        self.next = other
    def __repr__(self):
        return f'Val = {self.val}\nDepth = {self.depth}'
