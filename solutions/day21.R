# print(paste("Answer 2:", answer2))
# !/usr/bin/r

library(logging)
basicConfig()
addHandler(writeToConsole, logger = "test")


library(R6)

raw_input <- readLines("inputs/day21.txt")
processed <- gsub("^Player\\s(\\d)[^0-9]+(\\d+)$", "\\1 \\2", raw_input)
processed <- setNames(as.integer(substr(processed, 3, 4)), substr(processed, 1, 1))

clock_mod <- function(dividend, divisor) {
  ifelse(dividend %% divisor == 0, divisor, dividend %% divisor)
}


Player <- R6Class(public = list(
  score = 0,
  pos = NA_integer_,
  initialize = function(start) {
    self$pos <- start
  }
))

DiracGame <- R6::R6Class("DiracGame",
  public = list(
    last_val = 0,
    players = NULL,
    n_players = NA_integer_,
    die_divisor = 100,
    turn_divisor = 10,
    turn = 0,
    initialize = function(positions) {
      self$players <- lapply(positions, \(x) Player$new(x))
      self$n_players <- length(self$players)
      invisible(self)
    },
    print = function() {
      cat("Player 1 position:", self$players[[1]]$pos, sep = "\n")
      cat("Player 2 position:", self$players[[2]]$pos, sep = "\n")
      cat("Player 1 score:", self$players[[1]]$score, sep = "\n")
      cat("Player 2 score:", self$players[[2]]$score, sep = "\n")
      cat("Turn", self$turn, sep = "\n")
      invisible(self)
    },
    play = function(threshold = 1000) {
      last_score <- 0
      active <- 1
      while (last_score < threshold) {
        # browser()
        self$players[[active]]$pos <- private$advance(self$players[[active]]$pos, self$last_val)
        self$players[[active]]$score <- last_score <- self$players[[active]]$score + self$players[[active]]$pos
        self$turn <- self$turn + 3
        active <- (active %% self$n_players) + 1
      }
    },
    scores = function() sort(sapply(self$players, `[[`, "score"))
  ),
  private = list(
    # Update player position
    advance = function(pos, last_val) {
      forward <- private$get_forward(last_val)
      self$last_val <- clock_mod(self$last_val + 3, self$die_divisor)
      clock_mod(pos + forward, self$turn_divisor)
    },
    get_forward = function(last_val) {
      clock_mod(last_val + 1, self$die_divisor) +
        clock_mod(last_val + 2, self$die_divisor) +
        clock_mod(last_val + 3, self$die_divisor)
    }
  )
)

game <- DiracGame$new(positions = processed)
game$play(1000)
answer1 <- game$scores()[1] * game$turn


print(paste("Answer 1:", answer1))

# answer2 <- #TODO

# print(paste("Answer 2:", answer2))

`%c%` <- function(lhs, rhs) {
  if (is.na(lhs)) {
    rhs
  } else {
    lhs
  }
}

coalesce <- function(x, y) {
  ifelse(is.na(x), y, ifelse(is.na(y), x, x))
}
# answer1 <- #TODO

# print(paste("Answer 1:", answer1))

# answer2 <- #TODO

advances <- expand.grid(1:3, 1:3, 1:3) |>
  rowSums() |>
  tabulate()

# TODO get counts of next position given end for counts of sums of different rolls.
# and array tracking score
nonzero <- function(v) v[v != 0]

pathways <- expand.grid(1:10, which(advances != 0))
pathways <- cbind(
  pathways, clock_mod(rowSums(pathways), 10),
  advances[pathways[, 2]]
)
pathways
colnames(pathways) <- c("position", "roll", "end", "number")
pathways <- pathways[do.call(order, asplit(pathways, MARGIN = 2)), ]

library(dplyr)
simulate <- function(p1_start, p2_start, pathways, threshold = 21) {
  wins <- c("p1" = 0, "p2" = 0)
  state <- data.frame(expand.grid(player = 1:2, position = 1:10, score = 0:21))
  state$count <- ifelse(((state$position == p1_start & state$player == 1) | (state$position == p2_start & state$player == 2)) & state$score == 0, 1, 0)
  # Initialize starts with zero score
  i <- 1
  # browser()
  while (any(state$score < threshold)) {
    last <- state
    # For each player, advance each possible position by each possible roll value the correpsonding numebr of values, and update the state table accordingly.
    updated <- state |>
      subset(count > 0) |>
      merge(pathways, on = "position")
    updated$score <- updated$score + updated$end
    updated <- updated |>
      group_by(position, player, score) |>
      summarize(
        count = c(crossprod(count, number)),
        .groups = "drop"
      )
    # updated$count <- updated$count * updated$number
    # Add wins; multiply count by number of opposing player states that could have reached here
    if (any(updated$score >= threshold)) {
      # player 1: multiply by player 2 states in last turn
      wins["p1"] <- wins["p1"] + sum(updated$count[updated$player == 1 & updated$count >= threshold]) # * sum(last$count[last$player == 2])
      # player 2: multiply by winning states after excluding player 1 wins
      wins["p2"] <- wins["p2"] + sum(updated$count[updated$player == 2 & updated$score >= threshold]) # * sum(updated$count[updated$player == 1 & updated$score < threshold])
      updated <- updated[updated$score < threshold, ]
      # Break when all games simulated
      if (nrow(updated) == 0) {
        break
      }
    }

    state <- merge(state, updated[, c("position", "player", "score", "count")],
      by = c("position", "player", "score"), all.x =
        TRUE
    )
    # Coalesce updated counts column
    state$count <- ifelse(is.na(state$count.y), 0, state$count.y)
    state$count.x <- state$count.y <- NULL
    # print(state[state$count > 0, ])
    i <- i + 1
    # browser()
  }
  wins
}

answer2 <- simulate(4, 8, pathways)

print(paste("Answer 2:", answer2))
