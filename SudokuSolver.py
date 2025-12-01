import sys
import numpy as np
from sudoku import Sudoku
import json

def generate_puzzle(difficulty=0.5):
    puzzle = None
    while puzzle is None:                     # keep trying until valid
        puzzle = Sudoku(3).difficulty(difficulty)
    return puzzle


def board_to_numpy(board):
    clean = []
    for row in board:
        clean.append([cell if cell is not None else 0 for cell in row])
    return np.array(clean, dtype=int)

generated_grid = generate_puzzle(0.5)
sudoku_output = board_to_numpy(generated_grid.board)


sudoku_grid = np.empty((9, 9), dtype=object)

for r in range(9):
    for c in range(9):
        if(sudoku_output[r, c] > 0):
            sudoku_grid[r, c] = list()
            set_value = int(sudoku_output[r, c])
            sudoku_grid[r, c].append(set_value)
        else:
            sudoku_grid[r, c] = list(range(1, 10))  # Assign a new list to each cell

print(sudoku_grid)

# Access a specific cell and its list
print(f"\nList in cell (0, 0): {sudoku_grid[0, 0]}")
print(f"List in cell (4, 5): {sudoku_grid[4, 5]}")

print(sudoku_output)

def select_next(look_ahead_table):
    return look_ahead_table

with open("sudoku_output.json", "w") as f:
    json.dump(sudoku_output.tolist(), f)

