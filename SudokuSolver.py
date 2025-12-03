import sys
import numpy as np
from sudoku import Sudoku
import json
from flask import Flask, render_template, request

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

#calculates what cells are affected by cell (r, c)
#INPUT cell to check and output_grid of integers
#RETURNS a set of dependent cells
def calculate_dependent_cells(r, c, sudoku_grid):
    dependencies = set()

    #get dependent cells for the row and column
    for i in range(9):
        #checks it is is not its own cell and if the 
        if i != c and sudoku_grid[r, i] == 0: dependencies.add((r, i))
        if i != r and sudoku_grid[i, c] == 0: dependencies.add((i, c))

    #get the cells in the 3x3 grid in the cell
    #get the start row and column
    start_row = (r // 3) * 3
    start_col = (c // 3) * 3

    #check each in cell in the 3x3 space and add them
    for i in range(start_row, start_row+3):
        for j in range(start_col, start_col+3):
            
            if (i, j) != (r, c) and sudoku_grid[i, j] == 0:
                dependencies.add((i, j))
    
    return dependencies

#determines what cell to select next based on constraints
#1.Most Constrained (least constraints), 2.Most Constraining (most dependent_cells)
#INPUT look_ahead_table to check constraints and dependent_cells
#RETURNS (r, c) of cell to select next
def select_next(look_ahead_table, output_grid):
    #variables for most constrained selection
    most_constrained = list()
    min_constraints = 81

    for i in range(9):
        for j in range(9):
            #check if (i, j) has already been assigned
            if output_grid[i, j] == 0:
                #check if num of constraints is less than current min
                if len(look_ahead_table[i, j]['constraints']) < min_constraints:
                    most_constrained.clear()
                    most_constrained.append((i, j))
                    min_constraints = len(look_ahead_table[i, j]['constraints'])
                elif len(look_ahead_table[i, j]['constraints']) == min_constraints:
                    most_constrained.append((i, j))
                
    selected_cell = most_constrained[0]

    #from list check which cell is most constraining
    for cell in most_constrained:
        if len(look_ahead_table[cell]) > len(look_ahead_table[selected_cell]):
            selected_cell = cell
    
    return selected_cell

#check assigning a value for cell (r, c)
#checks every possible available constraint for the cell until one works
#checks how assigning a constraint affects the constraints of the dependent_cells
#makes sure the move leaves a possible constraint for every depependent cell
#INPUT cell (r, c) to check moves, look_ahead_table to use to check
#RETURNS number to assign (0 if no numbers worked)
def check_move(r, c, look_ahead_table):
    #the cell we are checking moves for
    cell = look_ahead_table[r, c]

    #iterates through contraints for cell
    for constraint_value in cell['constraints']:
        valid = True
        #checks the constraint against the constraints of the dependent_cells of cell
        for dCell in cell['dependent_cells']:
            row = dCell[0]
            col = dCell[1] 
            dependent_cell = look_ahead_table[row, col] 

            #only necessary check is to ensure that the dependent cell with 1 constraint
            #is not going to become invalidated with this move.
            #Other dependent cells with >1 constraints would still have at least 1 constraint left
            if (len(dependent_cell["constraints"]) == 1):
                if (dependent_cell["constraints"][0] == constraint_value):
                    valid = False
                    break

        if (valid):
            return constraint_value
    return 0

#assumes move will work
#sets num_to_assign to the output_grid cell (r, c)
#adjusts look_ahead_table constraints for (r, c) and it's dependent_cells
#INPUT cell (r, c), num_to_assign to (r, c), look_ahead_table, output_grid
def make_move(r, c, num_to_assign, look_ahead_table, output_grid):
    #set output_grid value to num_to_assign
    output_grid[r, c] = num_to_assign
    
    #update cell (r, c) constraints
    look_ahead_table[r, c]['constraints'] = [num_to_assign]

    #update dependent cell constraints
    for cell in look_ahead_table[r, c]['dependent_cells']:
        try:
            #print(f"{cell}, {cell[0]}, {cell[1]}")
            row = cell[0]
            col = cell[1]
            #print(look_ahead_table[row, col]['constraints'])
            look_ahead_table[cell[0], cell[1]]['constraints'].remove(num_to_assign)
        except:
            pass

    return


generated_grid = generate_puzzle(0.5)
sudoku_output = board_to_numpy(generated_grid.board)


sudoku_look_ahead_table = np.empty((9, 9), dtype=object)

for r in range(9):
    for c in range(9):

        dependent_cells = calculate_dependent_cells(r, c, sudoku_output)

        #create a dictionary for each cell
        #constraints are possible values for the cell
        #dependent_cells are cells that are affected by the value of cell (r, c)
        cell_data = {
            "constraints": [],
            "dependent_cells": dependent_cells
        }
        if(sudoku_output[r, c] > 0):
            set_value = int(sudoku_output[r, c])
            cell_data['constraints'].append(set_value)
        else:
            cell_data['constraints'] = list(range(1, 10))
        
        #assign the value to the cell in the look ahead table
        sudoku_look_ahead_table[r, c] = cell_data  # Assign a new list to each cell

#setting up every cell from initial grid
for r in range(9):
    for c in range(9):
        if(sudoku_output[r, c] > 0):
            make_move(r, c, int(sudoku_output[r, c]), sudoku_look_ahead_table, sudoku_output)


for r in range(9):
    for c in range(9):
        print(sudoku_look_ahead_table[r, c]['constraints'])


# Access a specific cell and its list
print(f"\nList in cell (0, 0): {sudoku_look_ahead_table[0, 0]['constraints']}")
print(f"List in cell (4, 5): {sudoku_look_ahead_table[4, 5]['constraints']}")

for r in range(9):
    for c in range(9):
        print(sudoku_look_ahead_table[r, c]['dependent_cells'])

cell_to_select = select_next(sudoku_look_ahead_table, sudoku_output)

print(cell_to_select)

print(sudoku_output)


with open("sudoku_output.json", "w") as f:
    json.dump(sudoku_output.tolist(), f)

