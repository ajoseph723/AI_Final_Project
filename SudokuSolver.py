import sys
import numpy as np

sudoku_grid = np.empty((9, 9), dtype=object)

for r in range(9):
    for c in range(9):
        sudoku_grid[r, c] = list(range(1, 10))  # Assign a new list to each cell


sudoku_output = np.zeros((9, 9))

print(sudoku_grid)

# Access a specific cell and its list
print(f"\nList in cell (0, 0): {sudoku_grid[0, 0]}")
print(f"List in cell (4, 5): {sudoku_grid[4, 5]}")

print(sudoku_output)


