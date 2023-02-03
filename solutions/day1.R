input <- readLines("inputs/day1.txt") |>
    as.integer()

part1 <- sum(diff(input) >= 1)
print(part1)

window <- 3
sums <- sapply(seq_len(length(input)), \(x) sum(input[seq(x, x + 2)], na.rm = TRUE))
part2 <- sum(diff(sums) >= 1)
print(part2)
