from collections import deque
from functools import reduce


def score(l):
    table = dict(zip(["(", "[", "{", "<"], range(1, 5)))
    return reduce(lambda x, y: (5 * x) + table[y], l, 0)


with open("inputs/day10.txt") as f:
    raw_input = f.read().split("\n")[:-1]


class CharCount:

    pairs = {
        ")": {"score": 3, "opener": "("},
        "]": {"score": 57, "opener": "["},
        ">": {"score": 25137, "opener": "<"},
        "}": {"score": 1197, "opener": "{"},
    }

    def __init__(self) -> None:

        self.record = {"(": 0, "[": 0, "<": 0, "{": 0}
        self.opened = deque()
        self.valid = True

    def __getitem__(self, char):
        # Open
        if char not in self.pairs.keys():
            # self.record[char]['count'] += 1
            self.opened.insert(0, char)
            return 0
        else:
            if self.pairs[char]["opener"] != self.opened[0]:
                self.valid = False
                return self.pairs[char]["score"]
            else:
                self.opened.popleft()
                return 0

    def __repr__(self) -> str:
        return self.record.__repr__()

    def __bool__(self):
        return self.valid


part1 = 0
processed = [deque(x) for x in raw_input]
valid = []
for i, line in enumerate(processed):
    record = CharCount()
    while line and record:
        char = line.popleft()
        part1 += record[char]
    if record and len(record.opened):
        valid.append(record.opened)

print(f"Answer 1 = {part1}")


scores = sorted([score(x) for x in valid])
part2 = scores[len(scores) // 2]
print(f"Answer 2 = {part2}")
