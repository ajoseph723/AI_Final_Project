from flask import Flask, render_template, request, jsonify
from SudokuSolver import generate_puzzle, board_to_numpy, calculate_dependent_cells, select_next, check_move, make_move

app = Flask(__name__)

@app.route('/')
def index():
    """Renders the HTML file."""
    return render_template('Frontend.html')

