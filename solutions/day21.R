play <- function(starts, threshold = 1000) {
    advance <- function(pos, last_val) {
        forward <- get_forward(last_val)
        last_val <<- clock_mod(last_val + 3, die_divisor)
        clock_mod(pos + forward, turn_divisor)
    }

    get_forward <- function(last_val) {
        clock_mod(last_val + 1, die_divisor) +
            clock_mod(last_val + 2, die_divisor) +
            clock_mod(last_val + 3, die_divisor)
    }

    die_divisor <- 100
    turn_divisor <- 10
    turn <- last_val <- 0
    players <- list(
        p1 = list(
            score = 0,
            pos = starts[[1]]
        ),
        p2 = list(
            score = 0,
            pos = starts[[2]]
        )
    )
    last_score <- 0
    active <- 1

    while (last_score < threshold) {
        players[[active]]$pos <-
            advance(players[[active]]$pos, last_val)
        players[[active]]$score <- last_score <- players[[active]]$score + players[[active]]$pos
        turn <- turn + 3
        active <- (active %% 2) + 1
    }
    turn * (sort(sapply(players, `[[`, "score")) |>
        min())
}

simulate <- function(p1_start, p2_start,
                     pathways,
                     threshold = 21) {
    advance_state <- function(state) {
        updated <- state |>
            subset(count > 0) |>
            merge(pathways, on = "position")
        updated[["position"]] <- updated[["end"]]
        updated[["count"]] <- updated[["count"]] * updated[["number"]]
        updated[["score"]] <- updated[["score"]] + updated[["end"]]
        updated
    }

    total_wins <- c("p1" = 0, "p2" = 0)
    player1 <- player2 <- expand.grid(position = 1:10, score = 0:21, count = 0)
    player1[player1[["score"]] == 0 & player1[["position"]] == p1_start, "count"] <- 1
    player2[player2[["score"]] == 0 & player2[["position"]] == p2_start, "count"] <- 1
    # Initialize starts with zero score

    while (nrow(player2) > 0) {
        # For each player, advance each possible position by each possible roll value the corresponding number of values, and update the state table accordingly.
        player1 <- advance_state(player1)
        if (nrow(player1) > 0) {
            wins <- player1[["score"]] > 20
            # Multiply number of winning states by current states for other player
            if (any(wins)) {
                total_wins[["p1"]] <-
                    total_wins[["p1"]] + sum(player1[wins, "count"]) * sum(player2[["count"]])
            }
            player1 <- player1[!wins, c("position", "score", "count")]
        }

        player2 <- advance_state(player2)
        if (nrow(player2) == 0) break
        wins <- player2[["score"]] > 20
        # Multiply number of winning states by current states for other player
        if (any(wins)) {
            total_wins[["p2"]] <-
                total_wins[["p2"]] + sum(player2[wins, "count"]) * sum(player1[["count"]])
        }
        player2 <- player2[!wins, c("position", "score", "count")]
    }
    total_wins
}


clock_mod <- function(dividend, divisor) {
    result <- dividend %% divisor
    result[result == 0] <- divisor
    result
}

raw_input <- readLines("inputs/day21.txt")
processed <- as.integer(gsub(".*\\s(\\d+)$", "\\1", raw_input))
names(processed) <- as.character(seq_along(processed))

print(play(starts = processed))

possibilities <- 1:3
advances <- expand.grid(possibilities, possibilities, possibilities) |>
    rowSums() |>
    tabulate()

pathways <- expand.grid(1:10, which(advances != 0))
pathways <- cbind(
    pathways, clock_mod(rowSums(pathways), 10),
    advances[pathways[, 2]]
)
colnames(pathways) <- c("position", "roll", "end", "number")
pathways <- pathways[do.call(order, asplit(pathways, MARGIN = 2)), ]


part2 <- simulate(processed[[1]], processed[[2]], pathways)
cat(as.character(max(part2)), "\n")
