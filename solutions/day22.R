# Unfinished in favor of day22.py, but retained for completeness

volume <- function(intervals) {
  prod(sapply(intervals, span))
}

span <- function(x) {
  if (length(x) == 0) {
    return(0)
  }
  x[[2]] - x[[1]] + 1
}

# Get shared volume of regions, processed pairwise in sequence
# Will this work? I think - find coordinates in common range

# Find overlapping portion of two intervals - zero-length if none
common_interval <- function(x, y) {
  # if(length(x) == 0 || length(y) == 0 || x[[2]] < y[[1]] || x[[1]] > y[[]]){
  # out <- integer()
  # }else if(x[[1]] <= y[[1]] && x[[2]] >= y[[2]]){
  # out <- y #y enclosed
  # }else if(x[[1]] > )
  if (length(x) == 0 || length(y) == 0) {
    return(integer())
  }
  common <- intersect(
    seq(from = x[[1]], to = x[[2]]),
    seq(from = y[[1]], to = y[[2]])
  )
  if (length(common) == 0) {
    return(common)
  }
  range(common)
}

# Return portions of intervals from list that overlap
overlap <- function(intervals) {
  if (length(intervals) == 1) {
    return(intervals)
  }
  Reduce(intervals, f = \(x, y){
    if (any(lengths(x)) == 0 || any(lengths(y)) == 0) {
      return(replicate(3, integer(), simplify = FALSE))
    }
    Map(common_interval, x, y)
  })
}

traverse_tree_list <- function(l, subscript){
    sub <- integer()
    for (num in subscript){
        sub <- c(sub, num )
        tryCatch(l[[sub]], 
                 error = function(e) l[[sub]]  <<- volume(overlap(processed[sub])),
                 finally = if(l[[sub]] == 0) return(0) 
                 )
    }

}

compute_on_volume <- function(instructions, on) {
  #ons <- sapply(instructions[on], volume) |> sum()
# No alternative to using tree structure
    # Add odd-numbered intersections, subtract even-numbered
  total <- if(on[[1]]) volume(instructions[[1]]) + if(on[[2]]) volume(instructions[[2]])-volume(overlap(instructions[1:2]))
  combs <- vector("list", length = instructions)
 
  #pairs <- combn(instructions, m = 2, FUN = \(x) volume(overlap(x))) |>
    #sum()
  total <- overlap(instructions) |>
    volume()
  ons - pairs + total
}

raw <- readLines("inputs/day22.txt")

# eval is a beast
processed <- gsub(pattern = "(-?\\d+)\\.{2}(-?\\d+)", replacement = "c(\\1, \\2)", raw)
on <- grepl("^on", processed)
processed <- gsub("^o[fn]+\\s(.*)", "list(\\1)", processed) |>
  lapply(\(x) eval(parse(text = x)))
part1_subset <- sapply(processed, \(x) max(abs(unlist(x))) <= 50)

compute_on_volume(processed[part1_subset], on[part1_subset])
