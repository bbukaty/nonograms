import os
import json
from solver import solvePuzzle, printPuzzle


def load_test_cases(folder_path):
    dir = os.listdir(folder_path)
    test_files = [file for file in dir if file.endswith('.json')]
    test_cases = []

    for file_name in test_files:
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r') as file:
            test = json.load(file)
            test["name"] = file_name
            test_cases.append(test)

    return test_cases


def run_test(test):
    print("~~~~~~~~~~~~~~~")
    print(f"Running test case {test['name']}:\n{test['description']}")
    height, width = test["size"]
    ourSolution = solvePuzzle(
        height, width, test["rowHints"], test["colHints"])
    solution = test["solution"]

    if are_2d_arrays_equal(ourSolution, solution):
        print("Passed ✅")
    else:
        print("Failed ❌")
        print("Expected:")
        printPuzzle(solution)
        print("Got:")
        printPuzzle(ourSolution)


def are_2d_arrays_equal(array1, array2):
    rows = len(array1)
    cols = len(array1[0])

    for i in range(rows):
        for j in range(cols):
            if array1[i][j] != array2[i][j]:
                return False

    return True


if __name__ == "__main__":
    test_folder = "puzzles"
    test_cases = load_test_cases(test_folder)
    for test in test_cases:
        run_test(test)
