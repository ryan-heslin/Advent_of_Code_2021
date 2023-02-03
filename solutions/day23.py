import sys
from collections import defaultdict
from copy import deepcopy
from itertools import repeat
from math import inf

test = len(sys.argv) > 1 and sys.argv[2] == "test"

values_map = {"A": 0, "B": 1, "C": 2, "D": 3}
letters = list(values_map.keys())
ends = {0, 10}


def parse(inp, xmax=10):
    stripped = inp[2 : (len(inp) - 1)]
    ymax = len(stripped)
    stripped.reverse()
    stripped = list(zip(*stripped))
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
            # Moving between hall rooms is illegal
            if (
                pos1 != pos2
                and not (pos1[1] == ymax and pos2[1] == ymax)
                and not (pos1[0] == pos2[0])
            ):
                # Permutations are treated differently
                for __ in range(2):
                    k = (pos1, pos2)
                    this = set()
                    # Add side rooms (if applicable)
                    # NB hall room above each side is counted, even though no amphi can stop there, so length of pathway is correct
                    # NB start (pos1) is not included
                    # BUG space above side rooms not counted
                    for i in range(pos1[1] + 1, ymax + 1):
                        this.add((pos1[0], i))
                    for i in range(pos2[1], ymax + 1):
                        this.add((pos2[0], i))
                    # Hall rooms: only add hall room with x-coord of stop position if stop is not in side room (in which case it would already have been added)
                    if pos1[0] < pos2[0]:
                        for i in range(pos1[0] + 1, pos2[0]):
                            this.add((i, ymax))
                    else:
                        for i in range(pos2[0] + 1, pos1[0]):
                            this.add((i, ymax))
                    pathways[k] = this
                    pos1, pos2 = pos2, pos1

    return pathways


def A_star(start, goal, debug=False):
    start_k = hash(start)
    open_set = {start_k: start}

    # For node k, node preceding it on cheapest known path to k
    came_from = {}

    # g_score[k] is cost of cheapest known path to k
    g_score = defaultdict(lambda: inf)
    g_score[start_k] = 0
    # gscore[k] + k.h() - best estimate of total cost (default to infinity if node unknown)
    f_score = defaultdict(lambda: inf)
    f_score[start_k] = g_score[start_k] + start.h()

    while open_set:
        min_cost = inf
        # h = hash
        current = None
        for h, node in open_set.items():
            score = f_score[h]
            this_cost = min(min_cost, score)
            if this_cost < min_cost and h in open_set.keys():
                current = node
                if current == goal:
                    return g_score[hash(current)]  # Cheapest cost to goal
                min_cost = this_cost
        current_k = hash(current)
        current.find_neighbors()
        if debug:
            print(hash(current))
            print(current)
            print("-------------------\n")
            for n in current.neighbors:
                print(n)
                print(current.d(n))
            input("Continue: ")
            print("\n\n\n")
        open_set.pop(current_k)
        for neighbor in current.neighbors:
            # print(neighbor.neighbors)

            # Distance from start to neighbor through current
            g_score_new = g_score[current_k] + current.d(neighbor)
            # print(f"distance: {current.d(neighbor)}")
            # print(neighbor)
            neighbor_k = hash(neighbor)
            # This path to neighbor cheaper than any known, so record it
            if g_score_new < g_score[neighbor_k]:
                came_from[neighbor_k] = current
                # New estimate of cost from this neighbor
                # Forgot this line
                g_score[neighbor_k] = g_score_new
                f_score[neighbor_k] = g_score_new + neighbor.h()
                if neighbor not in open_set.values():
                    open_set[neighbor_k] = neighbor


target = "tests" if test else "inputs"
with open(f"{target}/day23.txt") as f:
    inp = f.read().splitlines()

xmax = len(inp[0]) - 3
start, ymax = parse(inp, xmax=xmax)

positions = generate_positions(ymax=ymax)
paths = generate_pathways(positions)


class Factory:
    def __init__(self, pathways):
        self.pathways = pathways
        __class__.State.pathways = self.pathways

    class State:
        # pathways = paths
        sides_idx = {2, 4, 6, 8}
        wall = "#"
        empty = "."

        def __init__(self, mapping, xmax, ymax, *neighbors):
            self.neighbors_searched = False
            self.mapping = deepcopy(mapping)
            self.occupied = set()
            # Each side is a list of the amphipod types in that type's side room, padded with None if need be
            # Target: highest empty space
            # Completed: Number of correctly placed amphipods (i.e, all of side room type from bottom, no wrong types interposed)
            self.sides = {
                k: {"room": [None] * ymax, "target": inf, "completed": True}
                for k in self.mapping.keys()
            }
            # First open space in each side room; None if room full or contains amphipods of wrong type
            for k, v in self.mapping.items():
                self.occupied.update(v)
                for coord in v:
                    if coord[0] in __class__.sides_idx:
                        this_side = self.side_idx2type(coord[0])
                        # convert x coord back to amphipod value
                        self.sides[this_side]["room"][coord[1]] = k
                        # Lowest open space

            for k in self.sides.keys():
                # Equal to ymax if room full
                for i, amphi in enumerate(self.sides[k]["room"]):
                    if amphi != k:
                        if amphi is None:  # All squares above must also be empty
                            self.sides[k]["target"] = i
                        else:
                            self.sides[k]["completed"] = False
                        break
            self.xmax = xmax
            self.ymax = ymax
            self.neighbors = set()

        # Converts amphipod type (0, 1, 2, 3) to side room x-coordinate (2, 4, 6, 8)

        def draw_sides(self):
            out = []
            for i in range(self.ymax):
                char = " " if i == 0 else __class__.wall
                out.append(
                    [char] * 2
                    + [__class__.wall]
                    + [__class__.empty, __class__.wall] * len(__class__.sides_idx)
                    + [char] * 2
                )
            return out

        @staticmethod
        def type2side_coord(amphi):
            return amphi * 2 + 2

        # @lru_cache(maxsize=None)
        def __repr__(self):
            width = self.xmax + 3
            top = list(repeat(__class__.wall, width))
            hall = (
                [__class__.wall]
                + list(repeat(__class__.empty, self.xmax + 1))
                + [__class__.wall]
            )
            sides = self.draw_sides()
            bottom = (
                [" ", " "] + list(repeat(__class__.wall, self.xmax - 1)) + [" ", " "]
            )
            for k, v in self.mapping.items():
                char = letters[k]
                for coord in v:
                    if coord[1] == self.ymax:
                        hall[coord[0] + 1] = char
                    else:
                        sides[coord[1]][coord[0] + 1] = char
            sides.reverse()
            sides.insert(0, hall)
            sides.insert(0, top)
            sides.append(bottom)
            return "\n".join("".join(x) for x in sides)

        def __eq__(self, other):
            return self.mapping == other.mapping

        def __hash__(self):
            return int(
                "".join(
                    f"{str(k)}{self.tuple_string(v)}" for k, v in self.mapping.items()
                )
            )
            # Unique for each game state

        @staticmethod
        def tuple_string(data):
            return "".join("".join(str(y) for y in x) for x in sorted(data))

        def d(self, other):
            comp = other.mapping
            distance = 0
            # print(f"self: {self.mapping}")
            # print(f"other: {other.mapping}")
            for k, v in self.mapping.items():  # Trickier than I thought
                # Expect one amphi to be in a different position
                difference = tuple(v.symmetric_difference(comp[k]))
                assert len(difference) in {0, 2}
                # Should always be a single move separating the two states
                if len(difference) > 0:
                    distance += 10**k * (
                        len(__class__.pathways[(difference[0], difference[1])])
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
                                cost += 10**k * ((self.ymax - coord[1]) * 2 + 2)
                                # self.sides[k]["completed"] += 1
                                completed[k] += 1
                        else:
                            cost += (
                                len(__class__.pathways[(coord, (idx, completed[k]))])
                                * 10**k
                            )
                            # self.sides[k]["target"] += 1
                            completed[k] += 1
            # print(completed)
            return cost

        def add_neighbor(self, *args):
            # self.neighbors is set, so duplicates no issue
            # Caller shouldn't be neighbor of new because moves aren't reversible
            new = self.__class__(*args)
            self.neighbors.add(new)

        # Confirms path clear to target
        def validate_path(self, start, end):
            # Work around pathways including start space in some cases, which it never should
            return not (
                start == end
                or any(
                    space in self.occupied
                    for space in __class__.pathways[(start, end)].difference({start})
                )
                or end in self.occupied
            )

        # Find each neighbor of this game state on the graph - i.e., all game states one legal
        # move from this one
        # Known bugs:
        # 1. Pieces move into own side room which has other types
        # 2. Pieces move into empty side room of wrong type
        # 3. Fails to move piece of correct type into empty side room of correct type w/ clear path
        # 4. Illegal state with amphi ahead of None space
        # 5. Moves amphi in correct side room with no preceding amphis of wrong type
        def find_neighbors(self):
            if self.neighbors_searched:
                return

            copied = deepcopy(self.mapping)
            for k in copied.keys():  # Target is first open square in side room
                target = self.sides[k]["target"]
                idx = self.type2side_coord(k)
                # Can the relevant side room admit amphipods of this type?
                side_open = target < inf
                for coord in copied[k]:
                    # Case 1: path clear to target side room
                    # Must check if path clear to side room
                    # If target is ymax, room is full, so skip
                    # In any side, not necessarily correct one

                    # Skip if amphi already in correct room, or amphi in wrong room but blocked

                    if coord[0] in self.sides_idx:
                        x_type = self.side_idx2type(coord[0])
                        if (x_type == k and self.sides[k]["completed"]) or (
                            coord[1] < self.ymax - 1
                            and self.sides[x_type]["room"][coord[1] + 1] is not None
                        ):
                            continue
                    # Same case for starting side room and in hall room: always move to correct side room if possible
                    # Amphis in hall can only ever move to target side room
                    done = False
                    if side_open:
                        dest = (idx, target)
                        if self.validate_path(coord, dest):
                            copied[k].remove(coord)
                            copied[k].add(dest)
                            self.add_neighbor(deepcopy(copied), self.xmax, self.ymax)
                            copied[k].remove(dest)
                            copied[k].add(coord)
                            done = True

                    # Can move out of starting side room, but not to target side room
                    if not done and coord[1] != self.ymax:
                        for j in range(self.xmax + 1):
                            if j not in self.sides_idx:
                                this = (j, self.ymax)
                                if self.validate_path(coord, this):

                                    copied[k].remove(coord)
                                    copied[k].add(this)
                                    self.add_neighbor(
                                        deepcopy(copied), self.xmax, self.ymax
                                    )
                                    copied[k].remove(this)
                                    copied[k].add(coord)
            self.neighbors_searched = True

        # If correct side room open, move to it
        # Otherwise, try every open hall room


goal_mapping = {i: {(i * 2 + 2, j) for j in range(ymax)} for i in range(4)}

part1 = Factory(paths)
start = part1.State(start, xmax=xmax, ymax=ymax)
goal = part1.State(goal_mapping, xmax=xmax, ymax=ymax)


answer1 = A_star(start, goal, False)
print(f"Answer 1: {answer1}")

lengthened = inp[0:3] + ["  #D#C#B#A#", "  #D#B#A#C#"] + inp[3:]
xmax = len(lengthened[0]) - 3

start, ymax = parse(lengthened, xmax=xmax)

positions = generate_positions(ymax=ymax)
paths = generate_pathways(positions, ymax=ymax)

goal_mapping = {i: {(i * 2 + 2, j) for j in range(ymax)} for i in range(4)}

part2 = Factory(paths)

start = part2.State(start, xmax=xmax, ymax=ymax)
goal = part2.State(goal_mapping, xmax=xmax, ymax=ymax)
answer2 = A_star(start, goal, False)
print(f"Answer 2: {answer2}")
