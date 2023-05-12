import re
from math import copysign
from math import inf


def simulate(xvel, yvel):
    x = y = 0
    apogee = -inf
    x_sign = -copysign(1, xvel) * bool(xvel)
    hit = False

    while y >= YMIN or yvel > 0:
        x += xvel
        y += yvel
        apogee = max(y, apogee)
        xvel += x_sign
        x_sign *= bool(xvel)
        yvel -= 1
        if (not hit) and XMIN <= x <= XMAX and YMIN <= y <= YMAX:
            hit = True

    return apogee if hit else None


with open("inputs/day17.txt") as f:
    raw_input = f.read()

XMIN, XMAX, YMIN, YMAX = map(int, re.findall(r"-?\d+", raw_input))
apogees = [simulate(x, y) for x in range(XMAX + 1) for y in range(YMIN - 1, 2000)]

assert len(apogees)
apogees = [x for x in apogees if x is not None]
part1 = max(apogees)
part2 = len(apogees)


print(f"Answer 1 = {part1}")
print(f"Answer 2 = {part2}")
