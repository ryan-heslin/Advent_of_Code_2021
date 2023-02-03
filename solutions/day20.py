def create_matrix(nrow, ncol, val):
    return [[val] * (ncol) for __ in range(nrow)]


def pad_row(ncol, val):
    return [val for __ in range(ncol + 2)]


def pad_col(row, val):
    return [val] + row + [val]


def pad(mat, val):
    # Apply double layer of padding to each dimension
    return (
        [pad_row(len(mat[0]), val)]
        + [pad_col(row, val) for row in mat]
        + [pad_row(len(mat[0]), val)]
    )


# Kludge to swap values of outer padding
def switch(mat):
    reverse = {"0": "1", "1": "0"}
    return [
        [
            reverse[val] if j in (0, len(mat[0]) - 1) or i in (0, len(mat) - 1) else val
            for j, val in enumerate(row)
        ]
        for i, row in enumerate(mat)
    ]


def convolve(mat, lookup, inc=0, iterations=2):
    # ENHANCE!
    if inc == iterations:
        return mat
    mat = pad(mat, val=("0" if inc % 2 == 0 else "1"))
    out = create_matrix(len(mat), len(mat[0]), val="0" if inc % 2 == 0 else "1")
    inc += 1

    # Ignore padded edges when convolving pixels
    for i in range(1, len(mat) - 1):
        for j in range(1, len(mat[0]) - 1):
            val = "".join(
                [mat[k][l] for k in range(i - 1, i + 2) for l in range(j - 1, j + 2)]
            )
            number = int(val, base=2)
            out[i][j] = lookup[number]
    # Swap padding
    out = switch(out)
    return convolve(out, lookup, inc, iterations)


with open("inputs/day20.txt") as f:
    raw_input = f.read().split("\n")[:-1]

number = "".join(["0" if char == "." else "1" for char in raw_input.pop(0)])
lookup = {k: v for k, v in enumerate(number)}

digits = {".": "0", "#": "1"}
raw_input.pop(0)

nrow = len(raw_input)
ncol = len(raw_input[0])


matrix = create_matrix(nrow, ncol, val="0")


for i in range(nrow):
    for j in range(ncol):
        matrix[i][j] = digits[raw_input[i][j]]

matrix = pad(matrix, "0")
convolved = convolve(matrix, lookup)
answer1 = sum(int(x) for row in convolved for x in row)
print(f"Answer 1 = {answer1}")

convolved = convolve(matrix, lookup, iterations=50)
answer2 = sum(int(x) for row in convolved for x in row)
print(f"Answer 2 = {answer2}")
