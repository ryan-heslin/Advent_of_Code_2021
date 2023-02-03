import re
from math import ceil
from math import floor


def add(lhs, rhs):
    temp = eval(lhs)
    temp.append(eval(rhs))
    return str(temp)


def split(num, pattern=r"(?!-)(\d{2,})"):
    if not (replace := re.findall(pattern, num)):
        return num, False
    replace = replace[0]
    div = float(replace) / 2
    sub = f"[{floor(div)}, {ceil(div)}]"
    num = re.sub(pattern, sub, num, 1)
    return num, True


# We all cheat sometimes
# Possible to match all nested pairs, get correct by counting brackets
def count_brackets(string):
    count = 0
    for i, char in enumerate(string):
        if char == "[":
            count += 1
        elif char == "]":
            count -= 1
        if count == 5:
            yield i
    yield None


def explode(num):
    # Kludge pattern has two groups, one for special case
    if (start := next(count_brackets(num))) is None:
        return num, False
    # Ending position - off by one?
    end = re.search(r"\]", num[start:]).end() + start - 1
    assert num[end] == "]"

    left_num, right_num = (int(x) for x in re.findall(r"\d+", num[start:])[0:2])
    if prev_num := re.findall(r"\d+", num[0:start]):
        sub = str(int(prev_num[-1]) + left_num)
        left = re.sub(r"\d+(?=[^\d]*$)", sub, num[0:start])
    else:
        left = num[0:start]
    if next_num := re.findall(r"\d+", num[(1 + end) :]):
        sub = str(int(next_num[0]) + right_num)
        right = re.sub(r"\d+", sub, num[(end + 1) :], 1)
    else:
        right = num[(end + 1) :]
    middle = "0"
    # Add appropriate commas
    middle = middle + "," if re.match(r"\d", right[0]) else middle
    middle = "," + middle if re.match(r"\d", left[-1]) else middle
    return left + middle + right, True


def find_magnitude(lst):
    if isinstance(lst, int):
        return lst
    else:
        first = find_magnitude((lst[0]))
        return 3 * first + 2 * find_magnitude(lst[1])


def process(nums):
    while len(nums) > 1:
        cur = [nums.pop(0)]
        cur.extend([nums[0]])
        cur = re.sub(r"'|\s", "", str(cur))
        nums[0] = cur

        while True:
            nums[0], has_exploded = explode(nums[0])
            if not has_exploded:
                nums[0], has_split = split(nums[0])
                if not has_split:  # Finish if neither operation performed
                    break
    return nums[0]


def find_largest(nums):
    highest_magnitude = 0

    for i, num1 in enumerate(nums):
        for j, num2 in enumerate(nums):
            if i != j:
                result = process([num1, num2])
                highest_magnitude = max(highest_magnitude, find_magnitude(eval(result)))
    return highest_magnitude


with open("inputs/day18.txt") as f:
    raw_input = f.read()

processed = raw_input.split("\n")[:-1]


summed = eval(process(processed.copy()))
magnitude = find_magnitude(summed)
print(f"Answer 1: {magnitude}")

answer2 = find_largest(processed)
print(f"Answer 2: {answer2}")
