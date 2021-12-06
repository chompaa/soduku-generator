from copy import deepcopy
from random import sample, shuffle
from typing import Union


class Solver:
  board: list
  boards: list[list]

  def __init__(self, board: list) -> None:
    self.board = board
    self.boards = []

  @staticmethod
  def find_empty(board: list) -> Union[tuple, None]:
    for row in range(len(board)):
      for col in range(len(board)):
        if board[row][col] == 0:
          return row, col

    return None

  @staticmethod
  def check_valid(board: list, row_idx: int, col_idx: int, num: int) -> bool:
    if num in set(board[row_idx]):
      return False

    for row in board:
      if row[col_idx] == num:
        return False

    # map the row to the first square in the subboard
    row_idx = (row_idx // 3) * 3
    # map the col to the first square in the subboard
    col_idx = (col_idx // 3) * 3

    # here, we check four squares we've already checked, but i don't see a
    # workaround
    for row in range(row_idx, row_idx + 3):
      for col in range(col_idx, col_idx + 3):
        if board[row][col] == num:
          return False

    return True

  def solve(self, board: list, stop: int) -> bool:
    next: Union[tuple, None] = self.find_empty(board)

    if not next:
      self.boards.append(board)
      return True
    else:
      row: int
      col: int
      row, col = next

    for n in range(1, 10):
      if self.check_valid(board, row, col, n):
        _board: list = deepcopy(board)
        _board[row][col] = n

        if self.solve(_board, stop) and len(self.boards) > stop:
          return True

    return False

  def get_solutions(self, stop: int) -> list:
    self.solve(self.board, stop - 1)

    return self.boards


class Generator:
  base: int = 3
  side: int = 9
  board: list[list]

  def __init__(self) -> None:
    self.board = [[0 for _ in range(self.side)] for _ in range(self.side)]
    self.fill()

  @classmethod
  def pattern(self, row: int, col: int) -> int:
    return ((self.base * (row % self.base) + row // self.base + col)
            % self.side)

  @staticmethod
  def shuffle(sub_base: range) -> list:
    return sample(sub_base, len(sub_base))

  def fill(self) -> None:
    sub_base: range = range(self.base)

    # shuffle the rows and columns
    rows: list = [i * self.base + row for i in self.shuffle(sub_base)
                  for row in self.shuffle(sub_base)]
    cols: list = [i * self.base + col for i in self.shuffle(sub_base)
                  for col in self.shuffle(sub_base)]
    nums: list = self.shuffle(range(1, self.side + 1))

    # produce our grid based on our shuffled baseline pattern
    self.board = [[nums[self.pattern(row, col)]
                   for col in cols] for row in rows]

  def get_filled_board(self) -> list:
    return self.board

  def get_problem_board(self, tol: int) -> list:
    zeros: int = 0

    rows: list = [row for row in range(self.side)]
    cols: list = [col for col in range(self.side)]

    positions: list = list()

    for i in rows:
      for j in cols:
        positions.append(tuple((i, j)))

    shuffle(positions)

    board = deepcopy(self.board)

    for pos in positions:
      if zeros == tol:
        break

      row: int
      col: int
      row, col = pos

      temp: int = board[row][col]
      board[row][col] = 0

      solver = Solver(board)

      if len(solver.get_solutions(2)) > 1:
        board[row][col] = temp
      else:
        zeros += 1

    return board

  @classmethod
  def expand_line(self, line: str) -> str:
    # joins start, middle intersections and ends for any base
    return (line[0] + line[5:9]
            .join([line[1:5] * (self.base - 1)] * self.base) + line[9:13])

  @classmethod
  def display_board(self, board: list) -> None:
    # inspired by
    # https://stackoverflow.com/questions/45471152/how-to-create-a-sudoku-puzzle-in-python
    line0: str = self.expand_line("╔═══╤═══╦═══╗")
    line1: str = self.expand_line("║ . │ . ║ . ║")
    line2: str = self.expand_line("╟───┼───╫───╢")
    line3: str = self.expand_line("╠═══╪═══╬═══╣")
    line4: str = self.expand_line("╚═══╧═══╩═══╝")

    # join symbols to a string
    symbol: str = " 123456789"
    nums: list = [[""] + [symbol[n] for n in row] for row in board]

    # column numbers ontop (to aid selection)
    col_nums: str = "   ".join([str(col + 1) for col in range(self.side)])

    print(f"    {col_nums}")
    print(f"  {line0}")
    for row in range(1, self.side + 1):
      # row numbers on the side
      print(f"{row} ", end="")
      print(
          "".join(
              n + s for n, s in zip(nums[row - 1],
                                    line1.split("."))))
      print([f"  {line2}", f"  {line3}", f"  {line4}"]
            [(row % self.side == 0) + (row % self.base == 0)])


if __name__ == "__main__":
  problem = Generator()

  Generator.display_board(problem.get_problem_board(45))
  Generator.display_board(problem.get_filled_board())
