input <- readLines("inputs/day1.txt") |>
    strtoi()

part1 <- sum(diff(input) >= 1)
print(part1)

window <- 3
sums <- vapply(seq_len(length(input)),
    \(x) sum(input[seq(x, x + 2)], na.rm = TRUE),
    FUN.VALUE = numeric(1)
)
part2 <- sum(diff(sums) >= 1)
print(part2)
