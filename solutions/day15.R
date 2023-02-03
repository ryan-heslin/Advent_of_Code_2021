#!/usr/bin/r
raw_input <- readLines("inputs/day15.txt") |>
    lapply(\(x) as.numeric(unlist(strsplit(x, "")))) |>
    Reduce(f = rbind) |>
    unname()

layer <- rbind(
    c(-1, 0),
    c(0, 1),
    c(1, 0),
    c(0, -1)
) |> t()

get_neighbors <- function(x, y, row_max, col_max, val) {
    layer <- rbind(
        c(0, 1, 0, -1),
        c(-1, 0, 1, 0)
    )
    # browser()
    coords <- t(c(x, y) + layer)
    coords <- coords[coords[, 1] > 0 & coords[, 1] <= row_max & coords[, 2] > 0 & coords[, 2] <= col_max, ]
    # convert to 1d index to index row of data frame
    coords[, 1] + col_max * (coords[, 2] - 1)
}

# graph <- lapply(
# seq_len(nrow(raw_input)),
# \(row) mapply(
# \(row, column) get_neighbors(
# x = row, y = column, nrow(raw_input), ncol(raw_input), val = raw_input[row, column]
# ),
# row,
# seq_len(ncol(raw_input)),
# SIMPLIFY = FALSE
# )
# )
coords <- data.frame(
    ro = c(row(raw_input)),
    co = c(col(raw_input)),
    danger = c(raw_input),
    min_dist = Inf
)
coords$neighbors <- mapply(get_neighbors,
    x = coords$ro, y = coords$co, nrow(raw_input), ncol(raw_input),
    val = coords$danger,
    SIMPLIFY = FALSE
)
coords[1, c("min_dist", "danger")] <- 0
current <- 1
traverse <- function(graph) {
    unvisited <- neighbors <- seq_len(nrow(graph))
    while (length(unvisited)) {
        # Get unvisited node w/ minimum distance, remove from unvisited list
        current <- unvisited[which.min(graph[unvisited, "min_dist"])]
        unvisited <- unvisited[-which.min(graph[unvisited, "min_dist"])]
        dist <- graph[current, "min_dist"]
        neighbors <- graph[current, "neighbors"][[1]]
        graph[neighbors, "min_dist"] <- pmin(dist + graph[neighbors, "danger"], graph[neighbors, "min_dist"])
        neighbors <- intersect(neighbors, unvisited)
        # neighbors <- neighbors[order(graph[neighbors, "min_dist"])]
        # Exit on visiting all
    }
    return(graph)
}

graph <- traverse(coords)
answer1 <- tail(graph, 1)$min_dist

expanded <- do.call(cbind, replicate(5, raw_input, simplify = FALSE))
expanded <- do.call(rbind, replicate(5, expanded, simplify = FALSE))
mask <- outer(rep(0:4, each = nrow(raw_input)), rep(0:4, each = ncol(raw_input)), `+`)
expanded <- expanded + mask
expanded[expanded > 9] <- expanded[expanded > 9] - 9

coords2 <- data.frame(
    danger = c(expanded),
    min_dist = Inf
)

coords2$neighbors <- mapply(get_neighbors,
    x = c(row(expanded)), y = c(col(expanded)), nrow(expanded), ncol(expanded),
    val = coords2$danger,
    SIMPLIFY = FALSE
)
print(paste("Answer 1:", answer1))

coords2[1, "min_dist"] <- 0
graph <- traverse(coords2)
answer2 <- tail(graph, 1)$min_dist
print(paste("Answer 2:", answer2))
