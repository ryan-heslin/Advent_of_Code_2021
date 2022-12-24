#!/usr/bin/r
raw_input <- readLines("inputs/day2.txt")

parse_env <- new.env()
parse_env$forward <- function(x) complex(1, x, 0)
parse_env$backward <- function(x) complex(1, -x, 0)
parse_env$up <- function(x) complex(1, 0, -x)
parse_env$down <- function(x) complex(1, 0, x)

parsed <- gsub("([a-z]+)\\s(\\d+)", "\\1(\\2)", raw_input, perl = TRUE) |>
  paste(collapse = " + ")

summed <- eval(parse(text = parsed), envir = parse_env)



answer1 <- Re(summed) * Im(summed)

aim <- 0
parse_env$forward <- function(x) complex(1, x, aim * x)
parse_env$up <- function(x) {
  aim <<- aim - x
  complex(1, 0, 0)
}
parse_env$down <- function(x) {
  aim <<- aim + x
  complex(1, 0, 0)
}
summed2 <- eval(parse(text = parsed), envir = parse_env)
answer2 <- Re(summed2) * Im(summed2)
print(paste("Answer 1:", answer1))
print(paste("Answer 2:", answer2))
