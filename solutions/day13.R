fold <- function(coords, fold_coords) {
    constant_dimension <- which(coords == 0) # stays the same
    fold_along <- which(fold_coords != 0) # changes
    fold_coord <- fold_coords[fold_along]
    to_fold <- which(coords[, fold_along] > fold_coord)
    subscript <- cbind(to_fold, fold_along)
    coords[subscript] <- (2 * fold_coord) - coords[subscript]
    coords
}

raw_input <- read.csv("inputs/day13.txt", header = FALSE)

col_names <- c("x", "y")
colnames(raw_input) <- col_names
coords <- raw_input[!is.na(raw_input[, "y"]), ] |>
    rapply(as.integer, how = "replace") |>
    as.matrix()

folds <- raw_input[is.na(raw_input[, "y"]), 1]
folds <- gsub("fold\\salong\\s", "", folds) |>
    strsplit("=") |>
    Reduce(f = rbind)

fold_coords <- matrix(0, nrow = nrow(folds), ncol = ncol(folds))
fold_coords[cbind(
    seq_len(nrow(folds)),
    match(folds[, 1], col_names)
)] <- as.integer(folds[, 2])

fold1 <- fold(coords, fold_coords[1, ])
answer1 <- nrow(fold1) - sum(duplicated(fold1))
print(answer1)

folded <- Reduce(asplit(fold_coords, 1), f = fold, init = coords) |>
    unique()

folded <- folded[, rev(seq(dim(folded)[2]))] + 1

answer2 <- matrix(0, nrow = max(folded[, 1]), ncol = max(folded[, 2]))
answer2[folded] <- 1
apply(answer2, 2, rev) |>
    t() |>
    image()
