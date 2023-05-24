class Coding:
    def __init__(self, keys):
        self.decoding = None
        self.coding = [{y for y in x} for x in keys.split(" ")]
        assert set(UNIQUE_LENGTHS.values()).issubset({len(x) for x in self.coding})

    def __getitem__(self, length):
        return list(filter(lambda x: len(x) == length, self.coding))

    def __repr__(self):
        return self.coding.__repr__()

    def unscramble(self):
        four = self[4].pop()
        seven = self[3].pop()
        one = self[2].pop()
        two_three_five = self[5]
        zero_six_nine = self[6]
        a = seven - four
        for run in zero_six_nine:
            diff = one - run
            if len(diff) == 1:
                c = diff  # is 6
                f = one - c
        for run in two_three_five:
            if len(diff := (run.difference(four).difference(seven))) == 1:
                g = diff
        for run in two_three_five:
            diff = run.difference(seven).difference(g)
            if len(diff) == 1:
                d = diff
                b = four.difference(seven).difference(d)
        e = self[7].pop().difference(g).difference(four).difference(seven)
        self.decoding = {
            a.pop(): "a",
            b.pop(): "b",
            c.pop(): "c",
            d.pop(): "d",
            e.pop(): "e",
            f.pop(): "f",
            g.pop(): "g",
        }

    def decrypt(self, run, master):
        run = "".join(sorted(self.decoding[letter] for letter in run))
        return master[run]


with open("inputs/day8.txt") as f:
    raw_input = f.read().split("\n")[:-1]

mapping = dict((x.split(" | ") for x in raw_input))

UNIQUE_LENGTHS = {1: 2, 4: 4, 7: 3, 8: 7}
lengths = [len(pattern) for v in mapping.values() for pattern in v.split(" ")]

answer1 = sum(x in UNIQUE_LENGTHS.values() for x in lengths)
print(f"Answer 1 = {answer1}")

master = dict(
    zip(
        [
            "abcefg",
            "cf",
            "acdeg",
            "acdfg",
            "bcdf",
            "abdfg",
            "abdefg",
            "acf",
            "abcdefg",
            "abcdfg",
        ],
        range(10),
    )
)

decoding = {x: None for x in ("a", "b", "c", "d", "e", "f", "g")}


answer2 = 0
for k, v in mapping.items():
    coding = Coding(k)
    coding.unscramble()
    answer2 += int("".join(str(coding.decrypt(x, master)) for x in v.split(" ")))

print(f"answer2 = {answer2}")
