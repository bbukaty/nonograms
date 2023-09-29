import os
from solver import solve_puzzle
from utils import *

def run_test(test_path):
    print("~~~~~~~~~~~~~~~")
    print(f"Loading {test_path}...")

    column_clues, row_clues = parse_pynogram_file(test_path)
    our_solution = solve_puzzle(row_clues, column_clues)

    # Check if there's an empty space in our solution
    print_puzzle(our_solution)
    success = not any(' ' in row for row in our_solution)
    return success


if __name__ == "__main__":
    test_dir = "data/puzzles"
    test_files = [file for file in os.listdir(test_dir) if file.endswith('.txt')]

    with open("data/nonogram_ids_sorted.txt") as f:
        puzzle_ids_sorted = [f"{line.strip()}.txt" for line in f.readlines()]
        test_files = [file_name for file_name in puzzle_ids_sorted if file_name in test_files]
    
    successful_solves = 0
    total_puzzles = len(test_files)

    for test_file in test_files:
        test_path = os.path.join(test_dir, test_file)
        if run_test(test_path):
            successful_solves += 1

    success_percentage = (successful_solves / total_puzzles) * 100
    print(f"\nResults: {successful_solves}/{total_puzzles} puzzles successfully solved ({success_percentage:.2f}%)")
