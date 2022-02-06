from functools import lru_cache
import re

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


def search(num, powers, maxes, constant_args):
    z = 0
    while True:
        for i in range(len(powers)):
            digit = num // powers[i]
            num = num % powers[i]
            # Update w with new digit and run next block with previous state
            z = block(w=digit, z=z, **constant_args[i])
            if z > maxes[i]:
                break
        yield z


def nonzero_subtract(num):
    while num:
        num -= 1
        if not "0" in str(num):
            yield num


def solve(powers, constant_args, maxes, num=10 ** 14):
    z = -1
    fun_gen = search(num, powers, maxes, constant_args)
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
                    z_min = (vals["c4"] * (last_z - x * (w + vals["c15"]))) / (
                        25 * x + 1
                    )
                    if not (z_min % 2 == 0 and z_min > -1):
                        continue
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
# funs = [wrap_block(constants) for constants in values]


# maxes = get_max_zs(0, values)
# powers = [10 ** i for i in range(13, -1, -1)]
# answer1 = solve(powers, values, maxes)
# print(f"Answer 1: {answer1}")


# My approach when I worked backwards was to not be too clever. Try all w (1-9) and all values of x (0-1) and compute the range of possible inverses for that scenario. Then run the operation forwards for the candidates and throw away the bad ones. (edited)
# [10:03 PM]
# My first approach before improving to the above was to instead brute force. We have a set of target z to reach. Loop over all w (1-9) and a large range of z (e.g. 0-1000000) and run the operation to see if it hits our set of target z. All inputs that work make up our new set of target z.
#
# It's unsatisfyingly slow, but it works. (edited)
# [10:10 PM]
# For both approaches, when you have the ok z values for every step you can just greedily pick the largest/smallest digit that hits a z that is ok (edited)
# January 25, 2022
#
