from functools import lru_cache


def last_as_int(line):
    return int(line.split(" ")[-1])


def find_lowest(zs, values, last_z, num):
    for w in range(1, 10):
        new_z = block(w, last_z, **values[0])
        if new_z in zs[0]:
            if len(zs) == 1:
                return num + [str(w)]
            out = find_lowest(zs[1:], values[1:], new_z, num + [str(w)])
            if out:
                return out


def validate_zs(constants):
    last = [set([0])]
    for vals in reversed(constants.values()):
        last.append(set())
        for last_z in last[-2]:  # last filled set
            for w in range(1, 10):
                for x in range(2):
                    # Solve for z
                    z_min = (
                        vals["c4"]
                        * (last_z - x * (w + vals["c15"]))
                        // (DIVISOR * x + 1)
                    )
                    z_max = z_min + vals["c4"]
                    # Add any valid z-values not already present for this iteration
                    last[-1].update(
                        filter(
                            lambda cand: int(((cand % MODULUS + vals["c5"])) != w) == x,
                            range(int(z_min), int(z_max)),
                        )
                    )
    return last


# z is positive definite
@lru_cache(maxsize=512)
def block(w, z, c4, c5, c15):
    x = int((z % MODULUS + c5) != w)
    return (z // c4) * (DIVISOR * x + 1) + (w + c15) * x


# Could not have been solved without the help of algmyr from Python discord, who suggested the approach I use to find z values

with open("inputs/day24.txt") as f:
    processed = f.read().splitlines()

length = len(processed)
n_chunks = 14
instr_length = length // n_chunks

constant_lines = [4, 5, 15]
constant_args = ["c4", "c5", "c15"]
DIVISOR = last_as_int(processed[9])
MODULUS = last_as_int(processed[21])
values = []

for x in range(0, length, instr_length):
    values.append(
        dict(
            zip(
                constant_args,
                [last_as_int(line) for line in (processed[x] for x in constant_lines)],
            )
        )
    )
    constant_lines = [x + instr_length for x in constant_lines]
values = {i: d for i, d in enumerate(values)}


zs = validate_zs(values)
del zs[-1]
zs.reverse()
last_z = 0
number = []

z = None
for i in range(n_chunks):
    new_w = None
    for w in range(1, 10):
        new_z = block(w, last_z, **values[i])
        if new_z in zs[i]:
            z = new_z
            new_w = w
    last_z = z
    number.append(str(new_w))

answer1 = int("".join(number))
print(f"Answer 1: {answer1}")


number = find_lowest(zs, list(values.values()), 0, [])
answer2 = int("".join(number))
print(f"Answer 2: {answer2}")
