import sys
from collections import defaultdict
from functools import cache
from math import inf
from queue import PriorityQueue

ASCII_A = ord("A")
N_ROOMS = 4
HALL_SIZE = N_ROOMS + 7
TRANSLATION = dict(zip(map(chr, range(ASCII_A, ASCII_A + N_ROOMS)), range(N_ROOMS)))


@cache
def to_char(num):
    return chr(num + ASCII_A)


@cache
def distance(x, y):
    return abs(x - y)


@cache
def replace_tuple(x, i, new):
    return x[:i] + (new,) + x[i + 1 :]


def find_indices():
    return dict(zip(range(N_ROOMS), (2 * (x + 1) for x in range(N_ROOMS))))


class Arrangement:
    # Movement
    _costs = dict(zip(range(N_ROOMS), (10**x for x in range(N_ROOMS))))

    # Each room to right of this hall index
    _room_indices = find_indices()
    _pathways = {}
    for room, idx in _room_indices.items():
        path = set()
        for i in range(idx, -1, -1):
            path.add(i)
            key = (idx, i)
            _pathways[key] = frozenset(path)

        path = set()
        for i in range(idx, HALL_SIZE):
            path.add(i)
            key = (idx, i)
            _pathways[key] = frozenset(path)

    # Store rooms with hall-adjacent space indexed 0

    def __init__(self, rooms, hall):
        self.rooms = rooms
        self.hall = hall
        # Ignoring spaces outside rooms

    def __eq__(self, other):
        return self.hall == other.hall and self.rooms == other.rooms

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
            elif amphi != room:
                return None

        return result

        # Also false if completely full

    # Side room index reachable from each hall room
    def reachable_from_hall(self, hall_idx):
        amphi = self.hall[hall_idx]
        result = self.room_ready(amphi)
        if result is not None and self.path_open(
            hall_idx, type(self)._room_indices[amphi]
        ):
            return result

    def path_open(self, start, end):
        iter_range = (
            range(start + 1, end + 1) if start < end else range(start - 1, end - 1, -1)
        )
        return all(self.hall[space] is None for space in iter_range)

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

        cls = type(self)

        if amphi is not None and self.path_open(
            cls._room_indices[room_idx], cls._room_indices[amphi]
        ):
            side_dest = self.room_ready(amphi)
        else:
            side_dest = None
        illegal = type(self)._room_indices.values()
        for room in range(HALL_SIZE):
            if room not in illegal and self.path_open(
                cls._room_indices[room_idx], room
            ):
                result.add(room)

        return index, result, side_dest

    def room_full(self, room_idx):
        return all(el == room_idx for el in self.rooms[room_idx])

    def h(self):
        cls = type(self)
        estimate = sum(
            distance(i, cls._room_indices[el]) * cls._costs[el]
            for i, el in enumerate(self.hall)
            if el is not None
        )

        for amphi, room in enumerate(self.rooms):
            position = cls._room_indices[amphi]
            for i, el in enumerate(room):
                if el is not None:
                    estimate += (el != amphi) * (
                        distance(position, cls._room_indices[el]) + i
                    )
        return estimate

    def __hash__(self) -> int:
        return hash((self.hall, self.rooms))

    def __lt__(self, other):
        return self.h() < other.h()

    def __repr__(self):
        wall = "#"
        space = "."
        top = wall * (HALL_SIZE + 2)
        hall = (
            wall
            + "".join(space if el is None else to_char(el) for el in self.hall)
            + wall
        )
        inset = " " * 2
        side = wall * 2

        rooms = []
        for level in range(len(self.rooms[0])):
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
        bottom = side + wall * (HALL_SIZE - 2) + side
        return "\n".join([top] + [hall] + rooms + [bottom])

    def neighbors(self) -> dict["Arrangement", int]:
        hall = self.hall
        rooms = self.rooms
        result = {}
        cls = type(self)

        for room_idx in range(N_ROOMS):
            if not self.room_full(room_idx):
                departing_idx, hall_dests, room_dest_idx = self.reachable_from_room(
                    room_idx
                )
                # Index of moving amphipod

                if hall_dests or (room_dest_idx is not None):
                    amphi = rooms[room_idx][departing_idx]
                    new_room = replace_tuple(rooms[room_idx], departing_idx, None)
                    new_rooms = replace_tuple(rooms, room_idx, new_room)
                    # New state for each hall space moved to
                    for dest in hall_dests:
                        new_hall = replace_tuple(hall, dest, amphi)
                        new_state = cls(rooms=new_rooms, hall=new_hall)
                        result[new_state] = (
                            distance(cls._room_indices[room_idx], dest)
                            + departing_idx
                            + 1
                        ) * cls._costs[amphi]
                    # Update destination room, if possible
                    if room_dest_idx is not None:
                        new_dest_room = replace_tuple(
                            rooms[amphi], room_dest_idx, amphi
                        )
                        new_rooms = replace_tuple(new_rooms, amphi, new_dest_room)
                        # Hall doesn't change
                        new_state = cls(rooms=new_rooms, hall=hall)
                        result[new_state] = (
                            distance(
                                cls._room_indices[room_idx], cls._room_indices[amphi]
                            )
                            + departing_idx
                            + room_dest_idx
                            + 2
                        ) * cls._costs[amphi]
        # From hall rooms
        for space_idx in range(HALL_SIZE):
            if (amphi := hall[space_idx]) is not None and (
                dest_idx := self.reachable_from_hall(space_idx)
            ) is not None:
                new_hall = replace_tuple(hall, space_idx, None)
                new_room = replace_tuple(self.rooms[amphi], dest_idx, amphi)
                new_rooms = replace_tuple(rooms, amphi, new_room)
                new = cls(rooms=new_rooms, hall=new_hall)
                result[new] = (
                    distance(cls._room_indices[amphi], space_idx) + dest_idx + 1
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


def A_star(start, goal, debug=False):
    queue = PriorityQueue()
    estimate = start.h()
    queue.put((estimate, start), block=False)

    # g_score[k] is cost of cheapest known path to k
    g_score = defaultdict(lambda: inf)
    g_score[start] = 0
    f_score = defaultdict(lambda: inf)
    f_score[start] = estimate

    while queue.qsize():

        _, current = queue.get(block=False)
        best = g_score[goal]
        if f_score[current] >= best or current == goal:
            # breakpoint()
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
            print("-------------------\n")
            print(current)
            input("Continue: ")
            print("\n\n\n")
        # print(new_neighbors)
        for neighbor, dist in new_neighbors.items():
            # Distance from start to neighbor through current
            g_score_new = g_score[current] + dist
            # This path to neighbor cheaper than any known, so record it
            if g_score_new < g_score[neighbor]:
                # New estimate of cost from this neighbor
                g_score[neighbor] = g_score_new
                estimate = neighbor.h()
                f_score[neighbor] = g_score_new + estimate
                queue.put((estimate, neighbor), block=False)

    return g_score[goal]


def solve(raw_input):
    parsed = parse(raw_input)
    empty_hall = (None,) * HALL_SIZE
    n_floors = len(parsed[0])
    start = Arrangement(parsed, empty_hall)
    goal_rooms = tuple((x,) * n_floors for x in range(N_ROOMS))
    goal = Arrangement(goal_rooms, empty_hall)
    return A_star(start, goal, False)


target = "inputs"
with open(f"{target}/day23.txt") as f:
    raw_input = f.read().splitlines()

part1 = solve(raw_input)
print(part1)

new_rows = """
  #D#C#B#A#
  #D#B#A#C#
"""
new_rows = new_rows[1:].splitlines()
insertion_point = 2
raw_input = (
    raw_input[: insertion_point + 1] + new_rows + raw_input[insertion_point + 1 :]
)
part2 = solve(raw_input)
print(part2)
