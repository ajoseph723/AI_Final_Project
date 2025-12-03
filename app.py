from flask import Flask, render_template, request, jsonify
from SudokuSolver import generate_puzzle, board_to_numpy, calculate_dependent_cells, select_next, check_move, make_move

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('Frontend.html')

@app.route('/sudoku_data')
def sudoku_data():
    puzzle = generate_puzzle()
    numpy_grid = board_to_numpy(puzzle.board)
    return jsonify(numpy_grid.tolist())

if __name__ == '__main__':
    app.run(debug=True)
