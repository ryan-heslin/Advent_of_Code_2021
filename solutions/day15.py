from collections import defaultdict
from functools import cache
from math import inf
from queue import PriorityQueue


def parse(lines):
    graph = {}
    xmin = ymin = 0
    xmax = len(lines[0]) - 1
    ymax = len(lines) - 1
    for j, line in enumerate(lines):
        for i, char in enumerate(line):
            graph[complex(i, j)] = int(char)
    return graph, (xmin, xmax), (ymin, ymax)


@cache
def clock_modulus(x):
    return (x % 10) + (x >= 10)


def expand(graph, n, xrange, yrange):
    row_mult = xrange[1] + 1
    col_mult = yrange[1] + 1
    xs = range(row_mult)
    ys = range(col_mult)
    result = {}

    for row in range(n):
        for col in range(n):
            addend = row + col
            ymin = (row_mult) * row
            xmin = (col_mult) * col

            for i in xs:
                for j in ys:
                    result[complex(xmin + i, ymin + j)] = clock_modulus(
                        graph[complex(i, j)] + addend
                    )

    return result


def make_l1(goal):
    def result(point):
        return abs(point.real - goal.real) + abs(point.imag - goal.imag)

    return result


def make_l2(goal):
    def result(point):
        return (point.real - goal.real) ** 2 + (point.imag - goal.imag) ** 2

    return result


def make_neighbors(xmin, xmax, ymin, ymax):
    @cache
    def result(point):
        points = set()
        re = point.real
        im = point.imag
        if re > xmin:
            points.add(point - 1)
        if re < xmax:
            points.add(point + 1)
        if im > ymin:
            points.add(point - 1j)
        if im < ymax:
            points.add(point + 1j)
        return points

    return result


def dijkstra(start, graph, goal, neighbors):
    i = 0

    dist = defaultdict(lambda: inf)
    dist[start] = 0

    Q = PriorityQueue()
    Q.put((dist[start], i, start), block=False)

    while Q.qsize():
        cost, _, current_node = Q.get(block=False)
        if current_node == goal:
            return cost

        for neighbor in neighbors(current_node):
            alt = dist[current_node] + graph[neighbor]
            if alt < dist[neighbor]:
                i += 1
                dist[neighbor] = alt
                Q.put((alt, i, neighbor), block=False)


with open("inputs/day15.txt") as f:
    raw_input = f.read().splitlines()

graph, xrange, yrange = parse(raw_input)
neighbors = make_neighbors(*xrange, *yrange)
start = 0
part1 = dijkstra(start, graph, complex(xrange[1], yrange[1]), neighbors)
print(part1)

factor = 5
xmax = ymax = (xrange[1] + 1) * factor - 1
expanded = expand(graph, factor, xrange, yrange)
neighbors = make_neighbors(0, xmax, 0, ymax)
part2 = dijkstra(start, expanded, complex(xmax, ymax), neighbors)
print(part2)
