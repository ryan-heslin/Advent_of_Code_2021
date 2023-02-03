
compare_distances <- function(X, Y) {
    compare <- function(x) {
        sum(X[["distances"]][[x[[1]]]]
        %in% Y[["distances"]][[x[[2]]]])
    }
    idx <- expand.grid(X = seq_along(X[["distances"]]), Y = seq_along(Y[["distances"]]))
    idx[["shared"]] <- apply(idx, MARGIN = 1, FUN = compare)
    idx[["match"]] <- idx[["shared"]] > 11
    idx
}

distance <- function(X) {
    lapply(seq_len(dim(X)[[2]]), \(x) colSums(abs(sweep(X,
        MARGIN = 1, STATS = X[, x]
    ))))
}

# Parse input, converting to column vectors
raw <- readLines("inputs/day19.txt")
raw <- raw[raw != ""]
processed <- split(raw, cumsum(grepl("--", raw))) |>
    lapply(`[`, i = -1) |>
    lapply(\(x) matrix(as.numeric(unlist(strsplit(x, ","))), nrow = 3))

# Finding the 24 valid rotations by brute force
permutations <- list(
    c(1, 2, 3), c(1, 3, 2), c(2, 1, 3),
    c(2, 3, 1),
    c(3, 2, 1),
    c(3, 1, 2)
)

negations <- lapply(list(
    c(1, 1, 1),
    c(-1, 1, 1),
    c(-1, -1, 1),
    c(-1, 1, -1),
    c(1, -1, 1),
    c(1, -1, -1),
    c(1, 1, -1),
    c(-1, -1, -1)
),
diag,
ncol = 3
)

# Processs list of transformations in sequence
transform <- function(X, rotations, translations) {
    for (i in rev(seq_along(rotations))) {
        X <- (rotations[[i]] %*% X) - translations[[i]]
    }
    X
}

finished <- list()
rotations <- lapply(negations, \(x) lapply(permutations, \(y) x[, y])) |>
    unlist(recursive = FALSE)
rotations <- rotations[sapply(rotations, det) == 1]

unprocessed <- lapply(seq_along(processed), \(x) list(
    coords = processed[[x]],
    distances = distance(processed[[x]]),
    rotation = NULL,
    translation = NULL,
    center = NULL,
    processed = FALSE
))
unprocessed[[1]][["center"]] <- matrix(c(0, 0, 0), nrow = 3)
unprocessed[[1]][["rotation"]] <- rotations[1] # identity
unprocessed[[1]][["translation"]] <- list(c(0, 0, 0))

unprocessed[[1]][["processed"]] <- TRUE

known <- list(unprocessed[[1]])
unprocessed[[1]] <- NULL
found <- as.data.frame(known[[1]][["coords"]])

while (length(unprocessed) > 0) {
    found_this_known <- list()
    for (i in seq_along(known)) {
        found_this_iter <- integer()
        for (j in seq_along(unprocessed)) {
            comparison <- compare_distances(known[[i]], unprocessed[[j]])
            common <- which(comparison[["match"]])
            if (length(common) > 0) {
                matches <- known[[i]][["coords"]][, unique(comparison[common, "X"])]
                targets <- unprocessed[[j]][["coords"]][, unique(comparison[common, "Y"])]
                stopifnot(ncol(matches) == ncol(targets))
                for (rot in rotations) {
                    rotated <- rot %*% targets
                    difference <- rotated - matches
                    # If solution correct, offset for all common columns will be the same
                    if (length(unique(c(difference))) == 3) {

                        # Compose with existing transformations
                        unprocessed[[j]][["rotation"]] <- c(known[[i]][["rotation"]], list(rot))
                        unprocessed[[j]][["translation"]] <- c(
                            known[[i]][["translation"]], list(difference[, 1])
                        )
                        # Since the center is in reference coordinates
                        unprocessed[[j]][["center"]] <- transform(
                            -difference[, 1],
                            known[[i]][["rotation"]],
                            known[[i]][["translation"]]
                        )
                        unprocessed[[j]][["processed"]] <- TRUE
                        # Indices of newly matched beacon not already tied to known coordinates
                        new_subscript <- setdiff(
                            seq_along(unprocessed[[j]][["distances"]]),
                            unique(comparison[common, "Y"])
                        )
                        new_beacons <- unprocessed[[j]][["coords"]][, new_subscript]
                        new_beacons <- transform(
                            new_beacons,
                            rotations = unprocessed[[j]][["rotation"]],
                            translations = unprocessed[[j]][["translation"]]
                        )
                        new_beacons <- as.data.frame(new_beacons)
                        new_beacons <- new_beacons[, !new_beacons %in% found]
                        found <- cbind(found, new_beacons)
                        found_this_iter <- c(found_this_iter, j)
                        break
                    }
                }
            }
        }
        new <- unprocessed[found_this_iter]
        unprocessed[found_this_iter] <- NULL
        found_this_known <- c(found_this_known, new)
    }
    known <- found_this_known
    finished <- c(finished, known)
}

answer1 <- ncol(found)
print(paste("Answer 1:", answer1))

centers <- lapply(finished, \(x) x[["center"]])
distances <- combn(centers, m = 2, FUN = \(x) sum(abs(x[[1]] - x[[2]])))
print(paste("Answer 2:", max(distances)))
