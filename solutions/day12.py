with open("inputs/day12.txt") as f:
    raw_input = f.read().split("\n")[:-1]


def unique(lst):
    out = []
    for x in lst:
        if x not in out:
            out.append(x)
    return out


pairs = [x.split("-") for x in raw_input]
nodes = {y for x in pairs for y in x}
neighbors = {node: [] for node in nodes}

# Create dict where each node is keyed to list of adjacent nodes
while pairs:
    this = pairs.pop()
    neighbors[this[0]].append(this[1])
    neighbors[this[1]].append(this[0])


class Node:
    def __init__(self, name, neighbors):
        self.name = name
        self.neighbors = neighbors
        self.visited = False
        self.big = self.name.isupper()

    def __repr__(self):
        return f"""{self.name} | {self.visited}
{self.neighbors}"""


class Cave:
    paths = []

    def __init__(self, rooms):
        self.rooms = {k: Node(k, v) for k, v in rooms.items()}

    def __getitem__(self, k):
        return self.rooms[k]

    def __repr__(self):
        return "\n".join(room.__repr__() for room in self.rooms.values())

    # Indebted to https://stackoverflow.com/questions/62656477/python-get-all-paths-from-graph
    def get_paths(self, node="start", traversed=None):
        if not traversed:
            traversed = []
        traversed.append(node)
        self.rooms[node].visited = True
        neighbors = [
            room
            for room in self.rooms[node].neighbors
            if self.rooms[room].big or room not in traversed
        ]
        # Exit if dead end (no adjacent big or unvisited small nodes)
        if not neighbors:
            return
        if node == "end":
            self.paths.append(traversed)
            return
        for neighbor in neighbors:
            self.get_paths(node=neighbor, traversed=traversed.copy())

    def get_paths2(self, node="start", traversed=None, doubled=False):
        if not traversed:
            traversed = []
        # if node in traversed:
        # doubled = True
        doubled = doubled or (not self.rooms[node].big and node in traversed)
        traversed.append(node)
        self.rooms[node].visited = True
        neighbors = [
            room
            for room in self.rooms[node].neighbors
            if self.rooms[room].big
            or (room not in traversed or (room != "start" and not doubled))
        ]
        # Exit if dead end (no adjacent big or unvisited small nodes)
        if not neighbors:
            return
        if node == "end":
            self.paths.append(traversed)
            return
        for neighbor in neighbors:
            self.get_paths2(node=neighbor, traversed=traversed.copy(), doubled=doubled)


cave = Cave(neighbors)
cave.get_paths()
answer1 = len(cave.paths)
print(f"Answer 1 = {answer1}")

cave2 = Cave(neighbors)
cave2.get_paths2()


answer2 = len(unique(cave2.paths))
print(f"Answer 2 = {answer2}")
