#!/usr/bin/r
raw_input <- readLines("inputs/day7.txt")

processed <- unlist(strsplit(raw_input, ",")) |>
  as.integer()

solution <- round(mean(processed)) |>
  rep(length(processed))

cost <- function(x, constant, start) {
  sum((abs(start - x * constant)))
}
answer1 <- optimize(cost, interval = range(processed), constant = rep(1, length(processed)), start = processed)$objective |>
  round()


sum_to_n <- function() {
  res <- c(0, 1)
  inner <- function(n) {
    if (n %% 1 != 0) {
      return(NA_real_)
    } else if (is.na(res[n + 1])) {
      if (length(res) < n + 1) {
        length(res) <<- n + 1
      }
      res[n + 1] <<- (n * (n + 1)) / 2
    }
    return(res[n + 1])
  }
  inner
}

summer <- sum_to_n()
cost2 <- function(x, constant, start) {
  solution <- abs(start - x * constant)
  sum(sapply(solution, summer))
}
answer2 <- sapply(seq(max(processed)), cost2, constant = rep(1, length(processed)), start = processed) |>
  min()

print(paste("Answer 1:", answer1))
print(paste("Answer 2:", answer2))
