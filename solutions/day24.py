import re
from functools import lru_cache
from math import floor

# Could not have been solved without the help of algmyr from Python discord, who suggested the approach I use to find z values

with open("inputs/day24.txt") as f:
    raw_input = f.readlines()

instr_length = len(raw_input) // 14

constant_lines = [4, 5, 15]
constant_args = ["c4", "c5", "c15"]
processed = [x.rstrip("\n") for x in raw_input]
values = []
for x in range(0, len(raw_input), instr_length):
    values.append(
        dict(
            zip(
                constant_args,
                [
                    int(re.match(r"^[^0-9\-]+(-?\d+)$", line).group(1))
                    for line in (processed[x] for x in constant_lines)
                ],
            )
        )
    )
    constant_lines = [x + instr_length for x in constant_lines]
# print(f"Answer 2 = {answer2}")
values = {i: d for i, d in enumerate(values)}

# z is positive definite
@lru_cache(maxsize=512)
def block(w, z, c4, c5, c15):
    x = int((z % 26 + c5) != w)
    z = (z // c4) * (25 * x + 1) + (w + c15) * x
    return z


def search(num, powers, constant_args):
    z = 0
    while True:
        for i in range(len(powers)):
            digit = num // powers[i]
            num = num % powers[i]
            # Update w with new digit and run next block with previous state
            z = block(w=digit, z=z, **constant_args[i])
        yield z


def nonzero_subtract(num):
    while num:
        num -= 1
        if not "0" in str(num):
            yield num


def solve(powers, constant_args, num=10**14):
    z = -1
    fun_gen = search(num, powers, constant_args)
    num_gen = nonzero_subtract(num)
    while z != 0:
        z = next(fun_gen)
        num = next(num_gen)
        fun_gen.send(num)
    return num


"""Find the maximum possible z value in each block of the function in order to end with z = 0"""


def get_max_zs(prev, argsets):
    maxes = {}
    n = len(argsets) - 1
    for k, v in reversed(argsets.items()):
        max_z = 0
        # Have to reverse indices here, since this is working backwards of order blocks are actually run
        for w in range(1, 10):
            for z in range(prev, (prev * 10) + 10000):
                new = block(w, z, **v)
                max_z = z if new == prev else max_z
        maxes[n - k] = prev = max_z
    return maxes


def validate_zs(constants):
    last = [set([0])]
    for vals in reversed(constants.values()):
        last.append(set())
        for last_z in last[-2]:  # last filled set
            for w in range(1, 10):
                for x in range(2):
                    # Solve for z
                    z_min = floor(
                        vals["c4"] * (last_z - x * (w + vals["c15"])) / (25 * x + 1)
                    )
                    z_max = z_min + vals["c4"]
                    # Add any valid z-values not already present for this iteration
                    last[-1].update(
                        filter(
                            lambda cand: int(((cand % 26 + vals["c5"])) != w) == x,
                            range(int(z_min), int(z_max)),
                        )
                    )
    return last


# def find_highest(constants, zs)
# num = 0
# zs = reverse(zs)
# for i, constants in enumerate(constants):
# digits =


zs = validate_zs(values)
del zs[-1]
zs.reverse()
last_z = 0
number = []
for i in range(len(zs)):
    for w in range(1, 10):
        new_z = block(w, last_z, **values[i])
        if new_z in zs[i]:
            z = new_z
            new_w = w
    last_z = z
    number.append(str(new_w))

answer1 = int("".join(number))
print(f"Answer 1: {answer1}")


def find_lowest(zs, values, last_z, num):
    for w in range(1, 10):
        new_z = block(w, last_z, **values[0])
        if new_z in zs[0]:
            if len(zs) == 1:
                return num + [str(w)]
            out = find_lowest(zs[1:], values[1:], new_z, num + [str(w)])
            if out:
                return out
    else:
        return


number = find_lowest(zs, list(values.values()), 0, [])
answer2 = int("".join(number))
print(f"Answer 2: {answer2}")


powers = [10**i for i in range(13, -1, -1)]
