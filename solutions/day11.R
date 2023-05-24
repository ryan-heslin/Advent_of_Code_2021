get_neighbors <- function(coord, bounds = c(1, 10)) {
    neighbors <- t(coord + adjacent)
    neighbors[rowSums(neighbors < bounds[1] | neighbors > bounds[2]) == 0, ]
}

simulate <- function(grid, neighbors_index, find_sync = FALSE) {
    glowed <- i <- 0
    if (find_sync) {
        iterations <- Inf
    } else {
        iterations <- 100
    }

    dims <- prod(dim(grid))
    while (i < iterations) {
        grid[, ] <- complex(dims, Re(grid) + 1, 0)
        while (nrow(to_glow <- which(Re(grid) > 9 & Im(grid) == 0, arr.ind = TRUE)) > 0) {
            glowed <- glowed + nrow(to_glow)
            # Signal already glowed
            grid[to_glow] <- grid[to_glow] + 1i
            # Get neighbors, increment
            neighbors <- Reduce(f = rbind, neighbors_index[cbind(to_glow, 1)])
            neighbors <- neighbors[Im(grid[neighbors]) == 0, , drop = FALSE]
            # Get numbers of adjacencies
            if (length(neighbors) > 0) {
                increments <- ave(numeric(nrow(neighbors)), neighbors[, 1],
                    neighbors[, 2],
                    FUN = length
                )
                grid[neighbors] <- Re(grid[neighbors]) + increments
            }
        }
        # Reset
        grid[Im(grid) == 1] <- complex(length(grid[Im(grid) == 1]), 0, 0)
        i <- i + 1
        if (find_sync && all(grid == 0)) {
            return(i)
        }
    }
    glowed
}
raw_input <- readLines("inputs/day11.txt") |>
    strsplit("") |>
    sapply(as.numeric) |>
    t()

grid <- matrix(complex(
    prod(dim(raw_input)),
    raw_input, 0
), ncol = ncol(raw_input))

adjacent <- cbind(
    c(-1, 0), c(-1, 1), c(0, 1),
    c(1, 1), c(1, 0), c(1, -1),
    c(0, -1), c(-1, -1)
)
neighbors <- apply(which(Re(grid) > -1, arr.ind = TRUE), 1, get_neighbors) |>
    array(dim = c(10, 10, 1))


answer1 <- simulate(grid, neighbors)
print(paste("Answer 1:", answer1))

answer2 <- simulate(grid, neighbors, find_sync = TRUE)
print(paste("Answer 2:", answer2))
