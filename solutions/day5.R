draw <- function(coords, grid, row_mask, col_mask) {
    xes <- coords[, c(1, 3)]
    ys <- coords[, c(2, 4)]
    for (row in seq_len(nrow(coords))) {
        mask <- cbind(seq(ys[row, 1], ys[row, 2]), seq(xes[row, 1], xes[row, 2]))
        grid[mask] <- grid[mask] + 1
    }
    sum(grid > 1)
}

raw_input <- readLines("inputs/day5.txt")
processed <- gsub("\\s->\\s", ",", raw_input) |>
    strsplit(",") |>
    unlist() |>
    strtoi() |>
    matrix(ncol = 4, byrow = TRUE)

colnames(processed) <- c("x1", "y1", "x2", "y2")
processed <- processed + 1
dims <- sum(range(processed)) + 1
grid <- matrix(0, nrow = dims, ncol = dims)

row_mask <- row(grid)
col_mask <- col(grid)
non_diag <- processed[, "x1"] == processed[, "x2"] |
    processed[, "y1"] == processed[, "y2"]
part1 <- draw(processed[non_diag, ], grid, row_mask, col_mask)

part2 <- draw(processed, grid, row_mask, col_mask)

print(part1)
print(part2)
