#! /usr/bin/env python3

with open("inputs/day25.txt") as f:
    raw_input = f.read().split("\n")[:-1]

processed = [list(x) for x in raw_input]

# answer1 =
# print(f"Answer 1 = {answer1}")


class Trench:
    def __init__(self, grid):
        self.colmax = len(grid[0])
        self.rowmax = len(grid)
        self.grid = {}
        for i in range(self.rowmax):
            for j in range(self.colmax):
                self.grid[(i, j)] = {
                    "val": grid[i][j],
                    "e_neighbor": (i, (j + 1) % self.colmax),
                    "s_neighbor": ((i + 1) % self.rowmax, j),
                }

    def __repr__(self):
        return "".join(
            v["val"] if (i + 1) % (self.colmax) != 0 else v["val"] + "\n"
            for i, v in enumerate(self.grid.values())
        )

    def compare(self):
        return [v["val"] for v in self.grid.values()]

    def update(self):
        moved = i = 1
        while moved > 0:
            moved = 0
            new = {}
            for k, v in self.grid.items():
                if v["val"] == ">" and self.grid[v["e_neighbor"]]["val"] == ".":
                    new[k] = {
                        "val": ".",
                        "e_neighbor": v["e_neighbor"],
                        "s_neighbor": v["s_neighbor"],
                    }
                    new[v["e_neighbor"]] = {
                        "val": ">",
                        "e_neighbor": self.grid[v["e_neighbor"]]["e_neighbor"],
                        "s_neighbor": self.grid[v["e_neighbor"]]["s_neighbor"],
                    }
                    moved += 1
            self.grid.update(new)
            new = {}
            for k, v in self.grid.items():
                if v["val"] == "v" and self.grid[v["s_neighbor"]]["val"] == ".":
                    new[k] = {
                        "val": ".",
                        "e_neighbor": v["e_neighbor"],
                        "s_neighbor": v["s_neighbor"],
                    }

                    new[v["s_neighbor"]] = {
                        "val": "v",
                        "e_neighbor": self.grid[v["s_neighbor"]]["e_neighbor"],
                        "s_neighbor": self.grid[v["s_neighbor"]]["s_neighbor"],
                    }
                    moved += 1
            self.grid.update(new)
            i += 1
        return i - 1


grid = Trench(processed)
answer1 = grid.update()
print(f"Answer 1: {answer1}")
# answer2 =
# print(f"Answer 2 = {answer2}")
