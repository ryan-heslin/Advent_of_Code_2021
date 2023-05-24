cost <- function(x, constant, start) {
    sum(abs(start - x * constant))
}

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

cost_part2 <- function(x, constant, start) {
    solution <- abs(start - x * constant)
    sum(vapply(solution, summer, FUN.VALUE = numeric(1)))
}

raw_input <- readLines("inputs/day7.txt")
processed <- unlist(strsplit(raw_input, ",")) |>
    strtoi()

answer1 <- optimize(cost, interval = range(processed), constant = rep(1, length(processed)), start = processed)$objective |>
    round()


summer <- sum_to_n()
answer2 <- vapply(seq(max(processed)),
    cost_part2,
    constant = rep(1, length(processed)),
    start = processed,
    FUN.VALUE = numeric(1)
) |>
    min()

print(paste("Answer 1:", answer1))
print(paste("Answer 2:", answer2))
