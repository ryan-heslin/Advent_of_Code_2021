from copy import deepcopy
from functools import lru_cache
from math import inf

answer1 = 15 + 140 + 1300 + 12000
print(f"Answer 1: {answer1}")
answer2 = 47 + 420 + 3100 + 40000
print(f"Answer 2: {answer2}")


def parse(inp, xmax=10):
    stripped = inp[2 : (len(inp) - 1)]
    ymax = len(stripped)
    stripped.reverse()
    stripped = list(zip(*stripped))
    # chop off columns of #
    stripped = stripped[1 : (xmax + 1)]
    mapping = {i: set() for i in range(4)}
    for i in range(min(ends) + 2, max(ends) - 1, 2):
        this = stripped[i]
        for j in range(ymax):
            val = values_map[this[j]]
            mapping[val].add((i, j))  # Add position to set

    return mapping, ymax


def generate_positions(xmax=10, ymax=2):
    positions = set()
    for i in range(xmax + 1):
        if (
            i not in ends and i % 2 == 0
        ):  # side rooms (rooms above hallways not directly represented)
            for j in range(ymax):
                positions.add((i, j))
        else:  # hallway
            positions.add((i, ymax))
    return positions


# For tuple of positions (x, y), create list of
# spaces that must be empty to move from x to y (counting y but not x)
def generate_pathways(positions, ymax=2):
    pathways = {}
    for pos1 in positions:
        for pos2 in positions:
            if pos1 != pos2:
                # Permutations are treated differently
                for __ in range(2):
                    k = (pos1, pos2)
                    this = set()
                    # Add side rooms (if applicable)
                    # NB hall room above each side is counted, even though no amphi can stop there, so length of pathway is correct
                    # NB start (pos1) is not included
                    for i in range(pos1[1] + 1, ymax + 1):
                        this.add((pos1[0], i))
                    for i in range(pos2[1], ymax + 1):
                        this.add((pos1[0], i))
                    # Hall rooms: only add hall room with x-coord of stop position if stop is not in side room (in which case it would already have been added)
                    if pos1[0] < pos2[0]:
                        for i in range(pos1[0] + 1, pos2[0] + (pos2[1] == ymax)):
                            this.add((i, ymax))
                    else:
                        for i in range(pos2[0] + 1, pos1[0] + (pos1[1] == ymax)):
                            this.add((i, ymax))
                    # if pos1[1] < ymax - 1:  # Add side room squares
                    # for i in range(pos1[1] + 1, ymax):
                    # this.add((pos1[0], i))
                    # if pos2[1] < ymax - 1:
                    # for i in range(pos2[1] + 1, ymax):
                    # this.add((pos2[0], i))
                    ## TODO ensure all hall squares between are included, but not the starting position
                    # if pos1[1] == ymax:
                    # if pos1[0] < pos2[0]:
                    # start = pos1[0] + 1
                    # else:
                    # start = pos1
                    # xrange = sorted([pos1[0], pos2[0]])
                    #
                    # xrange[0] += 1  # Don't have to check starting space
                    # for i in range(*xrange):
                    # if i not in {2, 4, 6, 8}:
                    # this.add((i, ymax))
                    pathways[k] = this
                    pos1, pos2 = pos2, pos1

    return pathways


def A_star(start, goal):
    open_set = {start.__hash__(): start}

    came_from = {}
    g_score = {}
    g_score[start] = 0
    f_score = {}
    f_score[start] = start.h()

    while open_set:
        min_cost = inf
        for state, score in f_score:
            this_cost = min(min_cost, score)
            if this_cost < min_cost:
                current = state
                min_cost = this_cost
        if current == goal:
            return g_score[current]  # Cheapest cost to goal
        for neighbor in current.neighbors:
            g_score_new = g_score[current] + current.d(neighbor)
            if g_score_new < g_score[neighbor]:
                came_from[neighbor] = current
            f_score[neighbor] = g_score_new + neighbor.h()
            if neighbor not in open_set:
                open_set[neighbor] = neighbor


values_map = {"A": 0, "B": 1, "C": 2, "D": 3}
ends = {0, 10}

with open("inputs/day23.txt") as f:
    inp = f.read().splitlines()

xmax = len(inp[0]) - 2
start, ymax = parse(inp, xmax=xmax)

positions = generate_positions(ymax=ymax)
paths = generate_pathways(positions)


class State:
    pathways = paths
    sides_idx = {2, 4, 6, 8}

    def __init__(self, mapping, xmax, ymax, *neighbors):
        self.neighbors_searched = False
        self.mapping = deepcopy(mapping)
        self.occupied = set()
        # Each side is a list of the amphipod types in that type's side room, padded with None if need be
        # Target: highest empty space
        # Cimpleted: Number of correctly placed amphipods (i.e, all of side room type from bottom, no wrong types interposed)
        self.sides = {
            k: {"room": [None] * ymax, "target": None, "completed": None}
            for k in self.mapping.keys()
        }
        # First open space in each side room; None if room full or contains amphipods of wrong type
        for k, v in self.mapping.items():
            self.occupied.update(v)
            for coord in v:
                if coord[0] in __class__.sides_idx:
                    this_side = (coord[0] - 2) / 2
                    # convert x coord back to amphipod value
                    self.sides[this_side]["room"][coord[1]] = k
                    # Lowest open space

        for v in self.sides.values():
            # Equal to ymax if room full
            v["target"] = (
                max(i if amphi is not None else 0 for i, amphi in enumerate(v["room"]))
                + 1
            )
        self.xmax = xmax
        self.ymax = ymax
        self.neighbors = set([*neighbors])

    # Converts amphipod type (0, 1, 2, 3) to side room x-coordinate (2, 4, 6, 8)
    @staticmethod
    def type2side_coord(amphi):
        return amphi * 2 + 2

    # @lru_cache(maxsize=None)
    def __repr__(self):
        return self.mapping.__repr__()

    def __eq__(self, other):
        return self.mapping == other.mapping

    # @lru_cache(maxsize=None)
    def __hash__(self):
        return int(
            "".join(f"{str(k)}{self.tuple_string(v)}" for k, v in self.mapping.items())
        )
        # Unique for each game state

    @staticmethod
    def tuple_string(data):
        return "".join("".join(str(y) for y in x) for x in data)

    def d(self, other):
        comp = other.mapping
        distance = 0
        for k, v in self.mapping.items():  # Trickier than I thought
            # Expect one amphi to be in a different position
            difference = tuple(v.symmetric_difference(comp[k]))
            assert len(difference) <= 2
            if len(difference):
                distance += k * (
                    len(State.pathways[(difference[0], difference[1])])
                    + (difference[0][0] in State.sides_idx)
                    + (difference[1][0] in State.sides_idx)
                )
        return distance

    @staticmethod
    def side_idx2type(x):
        return (x - 2) / 2

    # @lru_cache(maxsize=None)
    def h(self):
        # Destination squares
        cost = 0
        # For each side room, highest index of amphipod in correct side room
        # This doesn't have to be updated
        start = {}
        for k, di in self.sides.items():
            i = 0
            while i < self.ymax and di["room"][i] == k:
                i += 1
            start[k] = i

        completed = start.copy()
        for k, v in self.mapping.items():
            for coord in v:
                idx = self.type2side_coord(k)
                if coord[0] in self.sides_idx:
                    # Has to leave side room and re-enter to clear way for wrong-type amphipod behind it
                    if coord[0] == self.type2side_coord(k):
                        if coord[1] > start[k]:
                            cost += 10 ** k * ((self.ymax - coord[1]) * 2 + 2)
                            # self.sides[k]["completed"] += 1
                            print("check")
                            completed[k] += 1
                    else:
                        cost += (
                            len(__class__.pathways[(coord, (idx, completed[k]))])
                            * 10 ** k
                        )
                        # self.sides[k]["target"] += 1
                        completed[k] += 1
        print(completed)
        return cost

    def add_neighbor(self, *args):
        # self.neighbors is set, so duplicates no issue
        # breakpoint()
        new = self.__class__(*args, self)
        # print(args)
        self.neighbors.add(new)
        # new.add_neighbor(self, *args)

    # Confirms path clear to target
    def validate_path(self, start, end):
        return not any(
            space in self.occupied for space in __class__.pathways[(start, end)]
        )

    # Find each neighbor of this game state on the graph - i.e., all game states one legal
    # move from this one
    def find_neighbors(self):

        for k in self.mapping.keys():  # Target is first open square in side room
            target = self.sides[k]["target"]
            idx = self.type2side_coord(k)
            # Can the relevant side room admit amphipods of this type?
            side_open = self.sides[k]["target"] < self.ymax - 1 and all(
                amphi == k for amphi in self.sides[k]["room"]
            )
            for coord in self.mapping[k]:
                # Case 1: path clear to target side room
                # Must check if path clear to side room
                # If target is ymax, room is full, so skip
                in_side = (
                    coord[0] in self.sides_idx
                    and coord[1]
                    == self.sides[self.side_idx2type(coord[0])]["target"] - 1
                )
                if side_open and self.validate_path(coord, (idx, target)):
                    # I guess this works?
                    self.mapping[k].remove(coord)
                    self.mapping[k].add((idx, target))
                    self.add_neighbor(deepcopy(self.mapping), self.xmax, self.ymax)
                    self.mapping[k].remove((idx, target))
                    self.mapping[k].add(coord)

                # Can move out of starting side room, but not to target side room
                elif not side_open and in_side:
                    for j in range(self.xmax + 1):
                        this = (j, self.ymax)
                        if self.validate_path(coord, this):

                            self.mapping[k].remove(coord)
                            self.mapping[k].add(this)
                            self.add_neighbor(
                                deepcopy(self.mapping), self.xmax, self.ymax
                            )
                            self.mapping[k].remove(this)
                            self.mapping[k].add(coord)
        self.neighbors_searched = True

        # If correct side room open, move to it
        # Otherwise, try every open hall room


goal_mapping = {i: {(i * 2 + 2, j) for j in range(ymax)} for i in range(4)}

start = State(start, xmax=xmax, ymax=ymax)
goal = State(goal_mapping, xmax=xmax, ymax=ymax)
