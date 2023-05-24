from math import inf
from math import prod


def hex2bin(string):
    # Credit https://stackoverflow.com/questions/3258330/converting-from-hex-to-binary-without-losing-leading-0s-python
    return (str(bin(int(string, 16))[2:])).zfill(len(string) * 4)


def base10(string):
    return int(string, base=2)


def parse(packet, digits):
    consumed, packet = packet[:digits], packet[digits:]
    return base10(consumed), packet


def parse_literal(packet):
    """Read 5-char chunks to the end of an integer packet. Returns computed value, remaining string, and characters consumed"""
    read = ""
    unfinished = True
    chars = 0
    while unfinished:
        unfinished = packet[0] == "1"
        consumed, packet = packet[1:5], packet[5:]
        read += consumed
        chars += 5
    return base10(read), packet, chars


def equals(lhs, rhs):
    return int(lhs == rhs)


def less(lhs, rhs):
    return int(lhs < rhs)


def greater(lhs, rhs):
    return int(lhs > rhs)


def identity(val):
    return val


class Operator:
    "Operator in expression tree: children are either Operators or values"
    operators = dict(enumerate([sum, prod, min, max, identity, greater, less, equals]))

    def __init__(self):
        self.type = self.version = self.value = 0
        self.children = []

    def add_child(self, children):
        self.children.extend(children)

    def __len__(self):
        return len(self.children)

    def __repr__(self):
        return f"Type: {self.type} Version: {self.version}\n{''.join(child.__repr__() for child in self.children)}"


def build_tree(digits, chars_left=inf, packets_left=inf):
    out = []
    while (
        min(chars_left, packets_left) > 0 and len(digits) > 10 and digits.count("1") > 0
    ):
        # Return if either consuming threshold reached, or if remaining digits are all 0 or too short to form a packet
        # Padding zeroes don't count in length
        node = Operator()
        version, digits = parse(digits, 3)
        type_id, digits = parse(digits, 3)
        node.version = version
        node.type = type_id
        chars_left -= 6

        if type_id == 4:
            value, digits, consumed = parse_literal(digits)
            node.value = value
            chars_left -= consumed
            packets_left -= 1
        else:
            length_id, digits = parse(digits, 1)
            chars_left -= 1
            chars = 15 if length_id == 0 else 11
            temp, digits = parse(digits, chars)
            chars_left -= chars
            prev = len(digits)

            if length_id == 0:
                new, digits = build_tree(digits, chars_left=temp)
            else:
                new, digits = build_tree(digits, packets_left=temp)
            packets_left -= 1
            chars_left -= prev - len(digits)
            node.add_child(new)

        out.append(node)
    return out, digits


def print_tree(root, indent=0, file="test.txt"):
    with open(file, "a") as f:
        f.writelines(
            f"{' ' * indent} Type: {root.type} | Version : {root.version} | Value: {root.value}\n"
        )
    for node in root.children:
        print_tree(node, indent + 2)


def evaluate(node):
    if node.type == 4:
        assert node.children == [] and node.value > -1
        return node.value
    assert node.value == 0
    for i, child in enumerate(node.children):
        node.children[i] = evaluate(child)

    # Binary or vector operation
    arg = node.children
    if node.type not in (5, 6, 7):
        arg = [arg]
    return node.operators[node.type](*arg)


with open("inputs/day16.txt") as f:
    raw_input = f.read().rstrip("\n")
digits = hex2bin(raw_input)
tree, _ = build_tree(digits)

answer2 = evaluate(tree[0])
answer1 = 0

tree, _ = build_tree(digits)
while tree:
    tree.extend(tree[0].children)
    cur = tree.pop(0)
    answer1 += cur.version

print(f"Answer 1: {answer1}")
print(f"Answer 2: {answer2}")
