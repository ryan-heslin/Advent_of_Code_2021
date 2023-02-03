import re


def compute_volume(instructions, on, part1):
    known = {}
    added = {}
    volume = 0
    for i, line in enumerate(instructions):
        added = {}
        if part1[i]:
            current = eval(line)
            for k, v in known.items():
                new = v.intersection(current)
                if new.volume != 0:
                    index = k + (i,)
                    added[index] = new
                    if (len(index)) % 2 == 0:
                        volume -= new.volume
                    else:
                        volume += new.volume
            # All added keys should be new
            if on[i]:
                added[(i,)] = current
                volume += current.volume  #  Only need single volume if ON cube
            known = {**known, **added}
    return volume


# Overlapping intervals
def overlap(x, y):
    out = [(None, None), (None, None), (None, None)]
    for i in range(3):
        if (
            None in x[i] or None in y[i] or x[i][1] < y[i][0] or x[i][0] > y[i][1]
        ):  # Disjoint
            out[i] = (None, None)
        elif x[i][0] <= y[i][0]:
            if x[i][1] <= y[i][1]:
                out[i] = (y[i][0], x[i][1])  # x[i] goes past left
            else:
                out[i] = y[i]  # y[i] contained in x[i]
        elif x[i][0] >= y[i][0]:
            if x[i][1] <= y[i][1]:
                out[i] = x[i]  # x[i] contained in y[i]
            else:
                out[i] = (x[i][0], y[i][1])  # x[i] goes past right
    return out


class Space:
    def __init__(self, x, y, z):
        self.coords = [x, y, z]
        self.spans = []
        volume = 1
        for pair in self.coords:
            if None in pair:
                self.spans = [(None, None), (None, None), (None, None)]
                volume = 0
                break
            new = pair[1] - pair[0] + 1
            volume *= new
            self.spans.append(new)
        self.volume = volume

    def intersection(self, other):
        if other is None:
            return self  # Reference semantics surprisingly didn't bite me this time
        if self.volume == 0:
            out = __class__((None, None), (None, None), (None, None))
        else:
            new = overlap(self.coords, other.coords)
            out = __class__(*new)
        return out

    def __repr__(self):
        return self.coords.__repr__() + "\nVolume: " + str(self.volume) + "\n"


with open("inputs/day22.txt") as f:
    raw_input = f.read().split("\n")[:-1]

processed = []
on = []
part1 = []

for line in raw_input:
    instr, line = line.split(" ")
    on.append(instr == "on")
    part1.append(max(abs(int(x)) for x in re.findall(r"-?\d+", line)) <= 50)
    line = re.sub(r"(-?\d+)\.{2}(-?\d+)", r"(\1,\2)", line)
    line = f"Space({line})"
    processed.append(line)


answer1 = compute_volume(processed, on, part1=part1)
print(f"Answer 1: {answer1}")

part1 = [True] * len(processed)

answer2 = compute_volume(processed, on, part1=part1)
print(f"Answer 2: {answer2}")
