# Hashable dict from https://stackoverflow.com/questions/6358481/using-functools-lru-cache-with-dictionary-arguments
class HashDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))


def extract_code(
    instr, ops={"add": "+", "mul": "*", "div": "//", "mod": "%", "eql": "=="}
):
    pattern = re.compile("^([a-z]{3}) ([wxyz]) (-?[0-9wxyz]+)$")
    matches = list(re.match(pattern, instr).groups())
    op = ops[matches[0]]
    eq = ("int(", ")") if op == "==" else ("", "")
    return f"{matches[1]} = {eq[0]}{matches[1]} {op} {matches[2]}{eq[1]}"


def constructor(code):
    @lru_cache(maxsize=None)
    def inner(state):
        exec(code)
        del state["x"]
        del state["y"]
        return state

    return inner


def search(num, funs, powers):

    state = HashDict({"z": 0})
    while True:
        for i in range(len(powers)):
            digit = num // powers[i]
            num = num % powers[i]
            # Update w with new digit and run next block with previous state
            state["w"] = digit
            state = funs[i](state)
        # breakpoint()
        yield state["z"]


def nonzero_subtract(num):
    num -= 1
    while "0" in str(num):
        num -= 1
    return num


def solve(funs, powers, num=10 ** 14):
    z = -1
    gen = search(num, funs, powers)
    while z != 0:
        z = next(gen)
        num = nonzero_subtract(num)
        gen.send(num)
    return num


# Parse each block of instructions into Python statements
code = [
    compile(
        "state['x'] =0; state['y'] =0;"
        + "; ".join(
            re.sub(r"(?<![a-z])([a-z])(?![a-z])", r"state['\1']", extract_code(y))
            for y in x
        ),
        "<string>",
        "exec",
    )
    for x in processed
]

powers = [10 ** i for i in range(13, -1, -1)]


functions = list(map(constructor, code))

answer1 = solve(functions, powers=powers)
