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

def calculate_dependent_cells(r, c, sudoku_grid):
    dependencies = set()

    #get dependent cells for the row and column
    for i in range(9):
        #checks it is is not its own cell and if the 
        if i != c and sudoku_grid[r, i] > 0: dependencies.add((r, i))
        if i != r and sudoku_grid[i, c] > 0: dependencies.add((i, c))

    #get the cells in the 3x3 grid in the cell
    #get the start row and column
    start_row = (r // 3) * 3
    start_col = (c // 3) * 3

    #check each in cell in the 3x3 space and add them
    for i in range(start_row, start_row+3):
        for j in range(start_col, start_col+3):
            
            if (i, j) != (r, c) and sudoku_grid[i, j] > 0:
                dependencies.add((i, j))
    
    return dependencies

generated_grid = generate_puzzle(0.5)
sudoku_output = board_to_numpy(generated_grid.board)


sudoku_look_ahead_table = np.empty((9, 9), dtype=object)

for r in range(9):
    for c in range(9):

        dependent_cells = calculate_dependent_cells(r, c, sudoku_output)

        #create a dictionary for each cell
        #canidates are possible values for the cell
        #dependent_cells are cells that are affected by the value of cell (r, c)
        cell_data = {
            "canidates": [],
            "dependent_cells": dependent_cells
        }
        if(sudoku_output[r, c] > 0):
            set_value = int(sudoku_output[r, c])
            cell_data['canidates'].append(set_value)
        else:
            cell_data['canidates'] = list(range(1, 10))
        
        #assign the value to the cell in the look ahead table
        sudoku_look_ahead_table[r, c] = cell_data  # Assign a new list to each cell

for r in range(9):
    for c in range(9):
        print(sudoku_look_ahead_table[r, c]['canidates'])


# Access a specific cell and its list
print(f"\nList in cell (0, 0): {sudoku_look_ahead_table[0, 0]['canidates']}")
print(f"List in cell (4, 5): {sudoku_look_ahead_table[4, 5]['canidates']}")

for r in range(9):
    for c in range(9):
        print(sudoku_look_ahead_table[r, c]['dependent_cells'])

print(sudoku_output)

def calculate_dependent_cells(r, c, sudoku_grid):
    dependencies = set()

    #get dependent cells for the row and column
    for i in range(9):
        #checks it is is not its own cell and if the 
        if i != c and sudoku_grid[r, i] > 0: dependencies.add((r, i))
        if i != r and sudoku_grid[i, c] > 0: dependencies.add((i, c))

    #get the cells in the 3x3 grid in the cell
    #get the start row and column
    start_row = (r // 3) * 3
    start_col = (c // 3) * 3

    #check each in cell in the 3x3 space and add them
    for i in range(start_row, start_row+3):
        for j in range(start_col, start_col+3):
            
            if (i, j) != (r, c) and sudoku_grid[i, j] > 0:
                dependencies.add((i, j))
    
    return dependencies

def select_next(look_ahead_table):

    return look_ahead_table

with open("sudoku_output.json", "w") as f:
    json.dump(sudoku_output.tolist(), f)

