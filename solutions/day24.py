from functools import lru_cache
import re

with open("inputs/day24.txt") as f:
    raw_input = f.readlines()

instr_length = len(raw_input) // 14

processed = [
    [y.rstrip("\n") for y in raw_input[(x + 1) : (x + instr_length)]]
    for x in range(0, len(raw_input), instr_length)
]


def extract_code(
    instr, ops={"add": "+", "mul": "*", "div": "//", "mod": "%", "eql": "=="}
):
    pattern = re.compile("^([a-z]{3}) ([wxyz]) (-?[0-9wxyz]+)$")
    matches = list(re.match(pattern, instr).groups())
    op = ops[matches[0]]
    eq = ("int(", ")") if op == "==" else ("", "")
    return f"{matches[1]} = {eq[0]}{matches[1]} {op} {matches[2]}{eq[1]}"


def constructor(code):
    cache = {}

    def inner(state):
        key = tuple(state.values())
        if key not in cache.keys():
            exec(code)
            cache[key] = state
        return cache[key]

    return inner


def constructor2(code):
    @lru_cache(maxsize=None)
    def inner(state):
        exec(code)
        return state

    return inner


def search(num, funs, powers):
    assert num < 10 ** 14

    state = {"x": 0, "y": 0, "z": 0}
    for i in range(len(powers)):
        digit = num // powers[i]
        num = num % powers[i]
        # Update w with new digit and run next block with previous state
        state["w"] = digit
        state = funs[i](state)
    return state["z"]


def nonzero_subtract(num):
    num -= 1
    while "0" in str(num):
        num -= 1
    return num


def solve(funs, powers, num=10 ** 14):
    z = -1
    while z != 0:
        num = nonzero_subtract(num)
        z = search(num, funs, powers)
    return num


# Parse each block of instructions into Python statements
code = [
    compile(
        "; ".join(
            re.sub(r"(?<![a-z])([a-z])(?![a-z])", r"state['\1']", extract_code(y))
            for y in x
        ),
        "<string>",
        "exec",
    )
    for x in processed
]

powers = [10 ** i for i in range(13, -1, -1)]


functions = list(map(constructor2, code))

answer1 = solve(functions, powers=powers)
# print(f"Answer 2 = {answer2}")


# def constructor(code):
# def inner(w, x, y, z):
# exec(code)
# return w, x, y, z
#
# return inner
# return inner
