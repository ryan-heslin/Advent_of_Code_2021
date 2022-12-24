#!/usr/bin/r
raw_input <- readLines("inputs/day5.txt")
processed <- gsub("\\s->\\s", ",", raw_input) |>
  strsplit(",") |>
  unlist() |>
  as.numeric() |>
  matrix(ncol = 4, byrow = TRUE)
colnames(processed) <- c("x1", "y1", "x2", "y2")
lines <- processed[processed[, "x1"] == processed[, "x2"] | processed[, "y1"] == processed[, "y2"], ] |> as.data.frame()
dims <- sum(range(processed)) + 1
grid <- matrix(0, nrow = dims, ncol = dims)

draw <- function(coords, row_mask, col_mask) {
  xes <- coords[c(1, 3)]
  ys <- coords[c(2, 4)]
  non_diag <- min(xes) == max(xes) || min(ys) == max(ys)
  if (non_diag) {
    mask <- which(row_mask <= max(ys) & row_mask >= min(ys) & col_mask <= max(xes) & col_mask >= min(xes), arr.ind = TRUE)
  } else {
    mask <- cbind(seq(ys[1], ys[2]), seq(xes[1], xes[2]))
  }
  grid[mask] <<- grid[mask] + 1
  invisible(NULL)
}
row_mask <- row(grid)
col_mask <- col(grid)
apply(lines, draw, MARGIN = 1, row_mask = row_mask, col_mask = col_mask)

answer1 <- sum(grid > 1)
grid[, ] <- 0
apply(processed, draw, MARGIN = 1, row_mask = row_mask, col_mask = col_mask)
answer2 <- sum(grid > 1)

print(paste("Answer 1:", answer1))
print(paste("Answer 2:", answer2))
