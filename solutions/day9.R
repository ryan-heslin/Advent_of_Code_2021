get_minima <- function(mat, coords, layer) {
    mapply(\(x, y) mat[x, y] < min(mat[t(c(x, y) + layer)]), coords[, 1], coords[, 2])
}

node <- function(coords, neighbors, valid) {
    # Generate list names of four neighboring points
    n_names <- lapply(neighbors, \(x) coords[1:2] + x) |>
        sapply(\(x) paste(x[1:2], collapse = ",")) |>
        intersect(valid)
    list(name = paste(coords[1:2], collapse = ","), val = coords[3], id = 0, visited = FALSE, neighbors = n_names)
}
expand_basin <- function(node, mapping, cur_id) {
    # Already visited
    if (node[["id"]] != 0) {
        return(node[["id"]])
    }
    # Add to current basin - only invoked recursively
    mapping[[node[["name"]]]][["id"]] <- cur_id
    neighbors <- lapply(node[["neighbors"]], get, envir = mapping)
    neighbors <- neighbors[sapply(neighbors, \(x) x[["id"]] == 0)]

    if (length(neighbors) == 0) {
        return()
    }
    lapply(neighbors, \(x) expand_basin(x, mapping, cur_id))
}
raw_input <- readLines("inputs/day9.txt")
processed <- sapply(raw_input, \(x) unlist(strsplit(x, "")), USE.NAMES = FALSE) |>
    t() |>
    `class<-`("integer")

pad <- max(processed) + 1
processed <- cbind(pad, processed, pad)
processed <- rbind(pad, processed, pad)
coords <- cbind(c(row(processed)[-c(1, nrow(processed)), -c(1, ncol(processed))]), c(col(processed)[-c(1, nrow(processed)), -c(1, ncol(processed))]))
coords <- cbind(coords, processed[coords])
layer <- rbind(
    c(-1, 0),
    c(0, 1),
    c(1, 0),
    c(0, -1)
) |> t()


minima <- get_minima(processed, coords, layer)
answer1 <- sum(coords[minima, ][, 3] + 1)

lookup <- setNames(0:9, as.character(0:9)) |>
    lapply(\(x) asplit(which(processed == x, arr.ind = TRUE), 1))

# Structrue representing point status, with "pointers" toa djacent nodes

coords <- coords[coords[, 3] < 9, ]
layer <- asplit(layer, 2)
rownames(coords) <- paste(coords[, 1], coords[, 2], sep = ",")
coords <- asplit(coords, 1)
mapping <- lapply(coords, \(x) node(x, neighbors = layer, valid = names(coords))) |>
    as.environment()

id <- 1
for (coord in names(coords)) {
    if (mapping[[coord]][["id"]] == 0 & mapping[[coord]][["val"]] < 9) {
        expand_basin(mapping[[coord]], mapping, id)
        id <- id + 1
    }
}

answer2 <- table(vapply(mapping, \(x) x[["id"]], FUN.VALUE = numeric(1))) |>
    sort(decreasing = TRUE) |>
    head(3) |>
    prod()

cat(answer1, "\n")
cat(answer2, "\n")
