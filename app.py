from flask import Flask, render_template, request, jsonify
from SudokuSolver import generate_puzzle, board_to_numpy, calculate_dependent_cells, make_move, completeStep, completeSudoku
import numpy as np
import threading

app = Flask(__name__)

solver_lock = threading.Lock()

puzzle = generate_puzzle()
sudoku_output = board_to_numpy(puzzle.board)

#look ahead table orgiginal setup
sudoku_look_ahead_table = np.empty((9, 9), dtype=object)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'action_button' in request.form:
            button_value = request.form['action_button']
            with solver_lock:
                if button_value == 'nextStep':
                    completeStep(sudoku_look_ahead_table, sudoku_output)
                elif button_value == 'finish':
                    completeSudoku(sudoku_look_ahead_table, sudoku_output)
    return render_template('Frontend.html')

@app.route('/sudoku_data')
def sudoku_data():

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
    
    #run make move to update the sudoku lookahead table
    for r in range(9):
        for c in range(9):
            if(sudoku_output[r, c] > 0):
                make_move(r, c, int(sudoku_output[r, c]), sudoku_look_ahead_table, sudoku_output)

    return jsonify(sudoku_output.tolist())

if __name__ == '__main__':
    app.run(debug=True)
