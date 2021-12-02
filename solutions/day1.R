input <- readLines("inputs/day1.txt") |>
  as.integer()

answer1 <- sum(diff(input) >= 1)

window <- 3
# input[length(input) + 1:2]  <- 0
sums <- sapply(seq_len(length(input)), \(x) sum(input[seq(x, x + 2)], na.rm = TRUE))
answer2 <- sum(diff(sums) >= 1)
