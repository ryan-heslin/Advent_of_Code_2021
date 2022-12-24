#!/usr/bin/r

    numbers <- readLines("inputs/day4.txt", n = 1)
    numbers <- unlist(strsplit(numbers, ",")) |>
      as.numeric()
    raw_input <- read.table("inputs/day4.txt", skip = 1) |>
      rapply(how = "replace", f = as.complex)

    board_dim <- 5
    boards <- array(t(as.matrix(raw_input)), dim = c(board_dim, board_dim, nrow(raw_input) / board_dim)) |>
      aperm(c(2, 1, 3))

    part1 <- function(boards, board_dim) {
      for (num in numbers) {
        boards[Re(boards) == num] <- boards[Re(boards) == num] + 0 + 1i
        col_sums <- colSums(Im(boards), dims = 1)
        # https://stackoverflow.com/questions/5135415/efficiently-compute-the-row-sums-of-a-3d-array-in-r
        # Apparently most efficient
        row_sums <- colSums(Im(aperm(boards, c(2, 1, 3))))
        if (length(winner_board <- which(colSums(row_sums == board_dim | col_sums == board_dim) != 0))) {
          print(winner_board)
          return(list(boards[, , winner_board], num))
        }
      }
    }
    winner_board <- part1(boards, board_dim)
    answer1 <- sum(Re(winner_board[[1]][Im(winner_board[[1]]) == 0])) * winner_board[[2]]


    print(paste("Answer 1:", answer1))

# Resorting to copypasta
    part2 <- function(boards, board_dim = 5, numbers) {
      for (num in numbers) {
        boards[Re(boards) == num] <- boards[Re(boards) == num] + 1i
        # Terminate with one board left
        col_sums <- colSums(Im(boards), dims = 1)
        # https://stackoverflow.com/questions/5135415/efficiently-compute-the-row-sums-of-a-3d-array-in-r
        # Apparently most efficient
        row_sums <- colSums(Im(aperm(boards, c(2, 1, 3))))
        drop <- which(colSums(row_sums == board_dim | col_sums == board_dim) != 0)

        if (length(drop)) {
          if (dim(boards)[3] == 1) {
            return(list(boards[, , 1], num))
          }
          boards <- boards[, , -drop, drop = FALSE]
        }
      }
    }
    result <- part2(boards, board_dim, numbers)
    winner_board <- result[[1]]
    winner_num <- result[[2]]
    answer2 <- sum(Re(winner_board[Im(winner_board) == 0])) * winner_num

    print(paste("Answer 2:", answer2))
