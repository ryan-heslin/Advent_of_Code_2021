import sys
from collections import defaultdict
from copy import deepcopy
from functools import cache
from itertools import combinations
from itertools import repeat
from math import inf
from queue import PriorityQueue
from time import sleep

ASCII_A = ord("A")
N_ROOMS = 4
HALL_SIZE = 7
TRANSLATION = dict(zip(map(chr, range(ASCII_A, ASCII_A + N_ROOMS)), range(N_ROOMS)))


def to_char(num):
    return chr(num + ASCII_A)


def replace_tuple(x, i, new):
    return x[:i] + (new,) + x[i + 1 :]


class Arrangement:
    # Movement
    _costs = dict(zip(range(N_ROOMS), (10**x for x in range(N_ROOMS))))
    # Precomputed distances to halls from each side room (outer space)
    # Index: side-hall
    # _dists = {
    #     (0, 0): 3,
    #     (0, 1): 2,
    #     (0, 2): 2,
    #     (0, 3): 4,
    #     (0, 4): 6,
    #     (0, 5): 8,
    #     (0, 6): 9,
    #     (1, 0): 5,
    #     (1, 1): 4,
    #     (1, 2): 2,
    #     (1, 3): 2,
    #     (1, 4): 4,
    #     (1, 5): 6,
    #     (1, 6): 7,
    #     (2, 0): 7,
    #     (2, 1): 6,
    #     (2, 2): 4,
    #     (2, 3): 2,
    #     (2, 4): 2,
    #     (2, 5): 4,
    #     (2, 6): 5,
    #     (3, 0): 9,
    #     (3, 1): 8,
    #     (3, 2): 6,
    #     (3, 3): 4,
    #     (3, 4): 2,
    #     (3, 5): 2,
    #     (3, 6): 3,
    # }

    # Each room to right of this hall index
    _room_indices = dict(zip(range(N_ROOMS), range(1, N_ROOMS + 1)))
    _pathways = {}
    _distances = {}
    # Distances among pairs of side rooms
    _room_distances = {
        combo: abs(combo[0] - combo[1]) * 2 + 1
        for combo in combinations(range(N_ROOMS), r=2)
    }
    for room, idx in _room_indices.items():
        path = set()
        for i in range(idx, -1, -1):
            path.add(i)
            key = (room, i)
            _pathways[key] = frozenset(path)
            _distances[key] = len(path) + 1

        path = set()
        for i in range(idx + 1, HALL_SIZE):
            path.add(i)
            key = (room, i)
            _pathways[key] = frozenset(path)
            _distances[key] = len(path) + 1

    # Store rooms with hall-adjacent space indexed 0

    def __init__(self, rooms, hall):
        self.depth = len(rooms[0])
        self.rooms = rooms
        self.hall = hall
        # Ignoring spaces outside rooms

    # Can side room receive amphipods of its type?
    # Indexed with 0 adjacent to hall
    # Check if path clear for both
    def room_ready(self, room):
        target_room = self.rooms[room]

        # Return empty space furthest from hall - one amphipods will move into
        result = None
        for i, amphi in enumerate(target_room):
            if amphi is None:
                result = i
            # Others present, so can't receive
            if amphi != room:
                return None

        return result

        # Also false if completely full

    # Side room index reachable from each hall room
    def reachable_from_hall(self, hall_idx):
        amphi = self.hall[hall_idx]
        result = self.room_ready(amphi)
        if result is not None and self.path_open(amphi, hall_idx):
            return result

    def path_open(self, amphi, hall_idx):
        cls = type(self)
        key = (amphi, hall_idx)
        return all(
            self.hall[space] is None or space == hall_idx
            for space in cls._pathways[key]
        )

    # Each hall or side room index reachable from side room
    def reachable_from_room(
        self,
        room_idx,
    ):
        result = set()
        room = self.rooms[room_idx]

        # Only continue if some wrong-type amphipods in room
        found = False
        amphi = index = None
        i = 0

        for i, el in enumerate(room):
            if el is not None:
                # If all amphis in room of correct type, no move possible
                if not found:
                    amphi = el
                    index = i
                    found = True
                if found and el != room_idx:
                    break
        else:
            return index, result, None

        side_dest = self.room_ready(amphi)
        for room in range(HALL_SIZE):
            if self.path_open(amphi, room):
                result.add(room)

        return index, result, side_dest

    def room_full(self, room_idx):
        return all(el == room_idx for el in self.rooms[room_idx])

    def h(self):
        return 0

    def __hash__(self) -> int:
        return hash((self.hall, self.rooms))

    def __lt__(self, other):
        return self.h() < other.h()

    def __repr__(self):
        wall = "#"
        space = "."
        extent = HALL_SIZE + N_ROOMS
        top = wall * (extent + 2)
        offsets = {0: 0, 1: 1, 2: 3, 3: 5, 4: 7, 5: 9, 6: 10}
        hall = list(space * extent)
        for i, el in enumerate(self.hall):
            if el is not None:
                hall[offsets[i]] = to_char(el)
        hall = wall + "".join(hall) + wall
        inset = " " * 2
        side = wall * 2

        rooms = []
        for level in range(self.depth):
            rooms.append(
                side
                + wall
                + wall.join(
                    space
                    if self.rooms[j][level] is None
                    else to_char(self.rooms[j][level])
                    for j in range(N_ROOMS)
                )
                + wall
                + side
            )
            side = inset
        bottom = inset + wall * (HALL_SIZE + 2) + inset
        return "\n".join([top] + [hall] + rooms + [bottom])

    def neighbors(self) -> dict["Arrangement", int]:
        hall = self.hall
        rooms = self.rooms
        result = {}
        cls = type(self)

        # breakpoint()
        for room_idx in range(N_ROOMS):
            if not self.room_full(room_idx):
                departing_idx, hall_dests, room_dest_idx = self.reachable_from_room(
                    room_idx
                )
                # Index of moving amphipod

                if hall_dests or room_dest_idx:
                    amphi = rooms[room_idx][departing_idx]
                    new_room = replace_tuple(rooms[room_idx], departing_idx, None)
                    new_rooms = replace_tuple(rooms, room_idx, new_room)
                    # New state for each hall space moved to
                    for dest in hall_dests:
                        new_hall = replace_tuple(hall, dest, amphi)
                        new_state = cls(rooms=new_rooms, hall=new_hall)
                        result[new_state] = (
                            cls._distances[(room_idx, dest)] + departing_idx
                        ) * cls._costs[amphi]
                    # Update destination room, if possible
                    if room_dest_idx:
                        new_dest_room = replace_tuple(
                            rooms[amphi], room_dest_idx, amphi
                        )
                        new_rooms = replace_tuple(new_rooms, amphi, new_dest_room)
                        # Hall doesn't change
                        new_state = cls(rooms=new_rooms, hall=hall)
                        result[new_state] = (
                            cls._room_distances[(room_idx, amphi)]
                            + departing_idx
                            + room_dest_idx
                        ) * cls._costs[amphi]
        # From hall rooms
        for space_idx in range(HALL_SIZE):
            if (amphi := hall[space_idx]) is not None and (
                dest_idx := self.reachable_from_hall(space_idx)
            ):
                new_hall = replace_tuple(hall, space_idx, None)
                new_room = replace_tuple(self.rooms[amphi], dest_idx, amphi)
                new_rooms = replace_tuple(rooms, amphi, new_room)
                new = cls(rooms=new_rooms, hall=new_hall)
                result[new] = (
                    cls._distances[(amphi, space_idx)] + target
                ) * cls._costs[amphi]

        return result


def parse(lines):
    result = [[] for _ in range(N_ROOMS)]
    for line in lines:
        letters = filter(str.isalpha, line)
        for i, char in enumerate(letters):
            result[i].append(TRANSLATION[char])

    return tuple(map(tuple, result))


debug = len(sys.argv) > 1 and sys.argv[1] == "-debug"
test = len(sys.argv) > 2 and sys.argv[2] == "-test"
print(debug)

VALUES_MAP = {"A": 0, "B": 1, "C": 2, "D": 3}
LETTERS = list(VALUES_MAP.keys())
ENDS = {0, 10}


def parse_old(inp, xmax=10):
    stripped = inp[2 : (len(inp) - 1)]
    ymax = len(stripped)
    stripped.reverse()
    stripped = list(zip(*stripped))
    stripped = stripped[1 : (xmax + 1)]
    mapping = {i: set() for i in range(4)}
    for i in range(min(ENDS) + 2, max(ENDS) - 1, 2):
        this = stripped[i]
        for j in range(ymax):
            val = VALUES_MAP[this[j]]
            mapping[val].add((i, j))  # Add position to set

    return mapping, ymax


def generate_positions(xmax=10, ymax=2):
    positions = set()
    for i in range(xmax + 1):
        if (
            i not in ENDS and i % 2 == 0
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
                for _ in range(2):
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
    queue = PriorityQueue()
    estimate = start.h()
    queue.put((estimate, start), block=False)

    # g_score[k] is cost of cheapest known path to k
    g_score = defaultdict(lambda: inf)
    g_score[start] = 0
    f_score = defaultdict(lambda: inf)
    f_score[start] = estimate
    visited = set()
    visited.add(start)

    while queue.qsize():

        _, current = queue.get(block=False)
        best = g_score[goal]
        if f_score[current] >= best or current == goal:
            continue
        new_neighbors = current.neighbors()
        # print(queue.qsize())
        if debug:
            print(hash(current))
            print(current)
            print("-------------------\n")
            for n, d in current.neighbors().items():
                print(n)
                print(d)
            input("Continue: ")
            print("\n\n\n")

        for neighbor, dist in new_neighbors.items():
            # breakpoint()
            print(neighbor)

            # Distance from start to neighbor through current
            g_score_new = g_score[current] + dist
            # print(f"distance: {current.d(neighbor)}")
            # print(neighbor)
            # This path to neighbor cheaper than any known, so record it
            if g_score_new < g_score[neighbor]:
                # New estimate of cost from this neighbor
                g_score[neighbor] = g_score_new
                estimate = neighbor.h()
                f_score[neighbor] = g_score_new + estimate
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.put((estimate, neighbor), block=False)

    return g_score[goal]


target = "inputs"
with open(f"{target}/day23.txt") as f:
    raw_input = f.read().splitlines()

parsed = parse(raw_input)
print(parsed)
empty_hall = (None,) * HALL_SIZE
n_floors = len(parsed[0])
start = Arrangement(parsed, empty_hall)
goal_rooms = tuple((x,) * n_floors for x in range(N_ROOMS))
goal = Arrangement(goal_rooms, empty_hall)
part1 = A_star(start, goal, True)
print(part1)

# xmax = len(inp[0]) - 3
# start, ymax = parse(inp, xmax=xmax)
#
# positions = generate_positions(ymax=ymax)
# paths = generate_pathways(positions)
#
#
# class Factory:
#     def __init__(self, pathways):
#         self.pathways = pathways
#         __class__.State.pathways = self.pathways
#
#     class State:
#         # pathways = paths
#         sides_idx = {2, 4, 6, 8}
#         wall = "#"
#         empty = "."
#
#         def __init__(self, mapping, xmax, ymax, *neighbors):
#             self.neighbors_searched = False
#             self.mapping = deepcopy(mapping)
#             self.occupied = set()
#             # Each side is a list of the amphipod types in that type's side room, padded with None if need be
#             # Target: highest empty space
#             # Completed: Number of correctly placed amphipods (i.e, all of side room type from bottom, no wrong types interposed)
#             self.sides = {
#                 k: {"room": [None] * ymax, "target": inf, "completed": True}
#                 for k in self.mapping.keys()
#             }
#             # First open space in each side room; None if room full or contains amphipods of wrong type
#             for k, v in self.mapping.items():
#                 self.occupied.update(v)
#                 for coord in v:
#                     if coord[0] in __class__.sides_idx:
#                         this_side = self.side_idx2type(coord[0])
#                         # convert x coord back to amphipod value
#                         self.sides[this_side]["room"][coord[1]] = k
#                         # Lowest open space
#
#             for k in self.sides.keys():
#                 # Equal to ymax if room full
#                 for i, amphi in enumerate(self.sides[k]["room"]):
#                     if amphi != k:
#                         if amphi is None:  # All squares above must also be empty
#                             self.sides[k]["target"] = i
#                         else:
#                             self.sides[k]["completed"] = False
#                         break
#             self.xmax = xmax
#             self.ymax = ymax
#             self.neighbors = set()
#
#         # Converts amphipod type (0, 1, 2, 3) to side room x-coordinate (2, 4, 6, 8)
#
#         def draw_sides(self):
#             out = []
#             for i in range(self.ymax):
#                 char = " " if i == 0 else __class__.wall
#                 out.append(
#                     [char] * 2
#                     + [__class__.wall]
#                     + [__class__.empty, __class__.wall] * len(__class__.sides_idx)
#                     + [char] * 2
#                 )
#             return out
#
#         @staticmethod
#         def type2side_coord(amphi):
#             return amphi * 2 + 2
#
#         # @lru_cache(maxsize=None)
#         def __repr__(self):
#             width = self.xmax + 3
#             top = list(repeat(__class__.wall, width))
#             hall = (
#                 [__class__.wall]
#                 + list(repeat(__class__.empty, self.xmax + 1))
#                 + [__class__.wall]
#             )
#             sides = self.draw_sides()
#             bottom = (
#                 [" ", " "] + list(repeat(__class__.wall, self.xmax - 1)) + [" ", " "]
#             )
#             for k, v in self.mapping.items():
#                 char = LETTERS[k]
#                 for coord in v:
#                     if coord[1] == self.ymax:
#                         hall[coord[0] + 1] = char
#                     else:
#                         sides[coord[1]][coord[0] + 1] = char
#             sides.reverse()
#             sides.insert(0, hall)
#             sides.insert(0, top)
#             sides.append(bottom)
#             return "\n".join("".join(x) for x in sides)
#
#         def __eq__(self, other):
#             return self.mapping == other.mapping
#
#         def __hash__(self):
#             # return hash((tuple(self.mapping.keys()), tuple(self.mapping.values())))
#             return int(
#                 "".join(
#                     f"{str(k)}{self.tuple_string(v)}" for k, v in self.mapping.items()
#                 )
#             )
#             # Unique for each game state
#
#         @staticmethod
#         def tuple_string(data):
#             return "".join("".join(str(y) for y in x) for x in sorted(data))
#
#         def d(self, other):
#             comp = other.mapping
#             distance = 0
#             # print(f"self: {self.mapping}")
#             # print(f"other: {other.mapping}")
#             for k, v in self.mapping.items():  # Trickier than I thought
#                 # Expect one amphi to be in a different position
#                 difference = tuple(v.symmetric_difference(comp[k]))
#                 assert len(difference) in {0, 2}
#                 # Should always be a single move separating the two states
#                 if len(difference) > 0:
#                     distance += 10**k * (
#                         len(__class__.pathways[(difference[0], difference[1])])
#                     )
#             return distance
#
#         @staticmethod
#         def side_idx2type(x):
#             return (x - 2) / 2
#
#         @cache
#         def h(self):
#             # Destination squares
#             return 0
#             cost = 0
#             # For each side room, highest index of amphipod in correct side room
#             # This doesn't have to be updated
#             start = {}
#             for k, di in self.sides.items():
#                 i = 0
#                 while i < self.ymax and di["room"][i] == k:
#                     i += 1
#                 start[k] = i
#
#             completed = start.copy()
#             for k, v in self.mapping.items():
#                 for coord in v:
#                     idx = self.type2side_coord(k)
#                     if coord[0] in self.sides_idx:
#                         # Has to leave side room and re-enter to clear way for wrong-type amphipod behind it
#                         if coord[0] == self.type2side_coord(k):
#                             if coord[1] > start[k]:
#                                 cost += 10**k * ((self.ymax - coord[1]) * 2 + 2)
#                                 # self.sides[k]["completed"] += 1
#                                 completed[k] += 1
#                         else:
#                             cost += (
#                                 len(__class__.pathways[(coord, (idx, completed[k]))])
#                                 * 10**k
#                             )
#                             # self.sides[k]["target"] += 1
#                             completed[k] += 1
#             # print(completed)
#             return cost
#
#         def __lt__(self, other):
#             return self.h() < other.h()
#
#         def add_neighbor(self, *args):
#             # self.neighbors is set, so duplicates no issue
#             # Caller shouldn't be neighbor of new because moves aren't reversible
#             new = self.__class__(*args)
#             self.neighbors.add(new)
#
#         # Confirms path clear to target
#         def validate_path(self, start, end):
#             # Work around pathways including start space in some cases, which it never should
#             return not (
#                 start == end
#                 or any(
#                     space in self.occupied
#                     for space in __class__.pathways[(start, end)].difference({start})
#                 )
#                 or end in self.occupied
#             )
#
#         # Find each neighbor of this game state on the graph - i.e., all game states one legal
#         # move from this one
#         def find_neighbors(self):
#             if self.neighbors_searched:
#                 return
#
#             copied = deepcopy(self.mapping)
#             for k in copied.keys():  # Target is first open square in side room
#                 target = self.sides[k]["target"]
#                 idx = self.type2side_coord(k)
#                 # Can the relevant side room admit amphipods of this type?
#                 side_open = target < inf
#                 for coord in copied[k]:
#                     # Case 1: path clear to target side room
#                     # Must check if path clear to side room
#                     # If target is ymax, room is full, so skip
#                     # In any side, not necessarily correct one
#
#                     # Skip if amphi already in correct room, or amphi in wrong room but blocked
#
#                     if coord[0] in self.sides_idx:
#                         x_type = self.side_idx2type(coord[0])
#                         if (x_type == k and self.sides[k]["completed"]) or (
#                             coord[1] < self.ymax - 1
#                             and self.sides[x_type]["room"][coord[1] + 1] is not None
#                         ):
#                             continue
#                     # Same case for starting side room and in hall room: always move to correct side room if possible
#                     # Amphis in hall can only ever move to target side room
#                     done = False
#                     if side_open:
#                         dest = (idx, target)
#                         if self.validate_path(coord, dest):
#                             copied[k].remove(coord)
#                             copied[k].add(dest)
#                             self.add_neighbor(deepcopy(copied), self.xmax, self.ymax)
#                             copied[k].remove(dest)
#                             copied[k].add(coord)
#                             done = True
#
#                     # Can move out of starting side room, but not to target side room
#                     if not done and coord[1] != self.ymax:
#                         for j in range(self.xmax + 1):
#                             if j not in self.sides_idx:
#                                 this = (j, self.ymax)
#                                 if self.validate_path(coord, this):
#
#                                     copied[k].remove(coord)
#                                     copied[k].add(this)
#                                     self.add_neighbor(
#                                         deepcopy(copied), self.xmax, self.ymax
#                                     )
#                                     copied[k].remove(this)
#                                     copied[k].add(coord)
#             self.neighbors_searched = True
#
#         # If correct side room open, move to it
#         # Otherwise, try every open hall room
#
#
# goal_mapping = {i: {(i * 2 + 2, j) for j in range(ymax)} for i in range(4)}
#
# part1 = Factory(paths)
# start = part1.State(start, xmax=xmax, ymax=ymax)
# goal = part1.State(goal_mapping, xmax=xmax, ymax=ymax)
#
#
# answer1 = A_star(start, goal, debug)
# print(f"Answer 1: {answer1}")
#
# lengthened = inp[0:3] + ["  #D#C#B#A#", "  #D#B#A#C#"] + inp[3:]
# xmax = len(lengthened[0]) - 3
#
# start, ymax = parse(lengthened, xmax=xmax)
#
# positions = generate_positions(ymax=ymax)
# paths = generate_pathways(positions, ymax=ymax)
#
# goal_mapping = {i: {(i * 2 + 2, j) for j in range(ymax)} for i in range(4)}
#
# part2 = Factory(paths)
#
# start = part2.State(start, xmax=xmax, ymax=ymax)
# goal = part2.State(goal_mapping, xmax=xmax, ymax=ymax)
# answer2 = A_star(start, goal, False)
# print(f"Answer 2: {answer2}")
# # Incorrect on some inputs; 50228 too high
