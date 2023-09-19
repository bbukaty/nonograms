import os
from solver import solvePuzzle
from utils import *

def run_test(test_path):
    print("~~~~~~~~~~~~~~~")
    print(f"Loading {test_path}...")

    # our solution
    column_clues, row_clues = parse_pynogram_file(test_path)
    ourSolution = solvePuzzle(row_clues, column_clues)
    # pynogram solution
    solution = []
    # compare

    print_puzzle(ourSolution)
    return

    if are_2d_arrays_equal(ourSolution, solution):
        print("Passed ✅")
    else:
        print("Failed ❌")
        print("Expected:")
        print_puzzle(solution)
        print("Got:")
        print_puzzle(ourSolution)


if __name__ == "__main__":
    test_dir = "data\puzzles"
    test_files = [file for file in os.listdir(test_dir) if file.endswith('.txt')]
    for test_file in test_files:
        test_path = os.path.join(test_dir, test_file)
        run_test(test_path)
        