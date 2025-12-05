import sys
import numpy as np
from sudoku import Sudoku
import json
import copy
from flask import Flask, render_template, request

def generate_puzzle(difficulty=0.9):
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
                if len(look_ahead_table[i, j]['constraints']) < min_constraints and len(look_ahead_table[i, j]['constraints']) != 0:
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
#checks max_iterations ahead (so checks max_iteration moves)
#uses valid_value_by_look_ahead
#INPUT cell (r, c) to check moves, look_ahead_table to use to check
#RETURNS number to assign (0 if no numbers worked)
def check_move(r, c, look_ahead_table, output_grid, current_iteration=0, max_iteration=5):
    #the cell we are checking moves for
    cell = look_ahead_table[r, c]

    #iterates through contraints for cell
    for constraint_value in cell['constraints']:
        look_ahead_table_copy = copy.deepcopy(look_ahead_table)
        output_grid_copy = output_grid.copy()
        if valid_value_by_look_ahead(r, c, constraint_value, look_ahead_table_copy, output_grid_copy, current_iteration, max_iteration):
            return constraint_value
    return 0


#checks every dependent_cell to make sure it will have valid constraints
#checks it hasn't checked so far the puzzle is complete
#selects next cell and then runs make move on that cell (checks next move)
def valid_value_by_look_ahead(r, c, constraint_value, look_ahead_table, output_grid, current_iteration, max_iteration):
    cell = look_ahead_table[r, c]

    if len(cell["dependent_cells"]) >= 1:

        #checks the constraint against the constraints of the dependent_cells of cell
        for dR, dC in cell["dependent_cells"]:
            dependent = look_ahead_table[dR, dC]

            #only necessary check is to ensure that the dependent cell with 1 constraint
            #is not going to become invalidated with this move.
            #Other dependent cells with >1 constraints would still have at least 1 constraint left
            if len(dependent["constraints"]) == 1:
                only_value = dependent["constraints"][0]
                if (only_value == constraint_value):
                    return False
            
    make_move(r, c, constraint_value, look_ahead_table, output_grid)
    
    if puzzleIsComplete(output_grid):
        return True
    
    if current_iteration <= max_iteration: 
        next_cell = select_next(look_ahead_table, output_grid)

        print(f"Iteration num - {current_iteration}: {next_cell}")
        current_iteration = current_iteration + 1
        print(f"constraints: {look_ahead_table[next_cell[0], next_cell[1]]["constraints"]}")
        print(f"dependents: {look_ahead_table[next_cell[0], next_cell[1]]["dependent_cells"]}")
        val_to_input = check_move(next_cell[0], next_cell[1], look_ahead_table, output_grid, current_iteration, max_iteration)
        
        if val_to_input == 0:
            return False
    
    
    return True
            

#assumes move will work
#sets num_to_assign to the output_grid cell (r, c)
#adjusts look_ahead_table constraints for (r, c) and it's dependent_cells
#INPUT cell (r, c), num_to_assign to (r, c), look_ahead_table, output_grid
def make_move(r, c, num_to_assign, look_ahead_table, output_grid):
    #set output_grid value to num_to_assign
    output_grid[r, c] = num_to_assign
    
    #update cell (r, c) constraints
    look_ahead_table[r, c]['constraints'] = list()

    #update dependent cell constraints and dependent_cells
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


def completeStep(look_ahead_table, output_grid):
    if (not puzzleIsComplete(output_grid)):
        try:
            next_cell = select_next(look_ahead_table, output_grid)
            print(next_cell)
            num_to_assign = check_move(next_cell[0], next_cell[1], look_ahead_table, output_grid)
            if (num_to_assign != 0):
                make_move(next_cell[0], next_cell[1], num_to_assign, look_ahead_table, output_grid)
                return True
            else:
                return False
        except:
            return False
    else:
        return False



def completeSudoku(look_ahead_table, output_grid):
    while(not puzzleIsComplete(output_grid)):
        completed = completeStep(look_ahead_table, output_grid)
        if (not completed):
            print("Exiting... No possible Moves")
            #sys.exit(1)


def puzzleIsComplete(output_grid):
    for r in range(9):
        for c in range(9):
            if (output_grid[r, c] == 0):
                return False
    
    return True
