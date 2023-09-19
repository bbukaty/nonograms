def print_puzzle(puzzle):
    """Takes 2d arr of strings, prints nonogram in ascii.
    TODO print hints above and beside puzzle
    """
    width = len(puzzle[0])
    print("┌" + "─┬" * (width - 1) + "─┐")
    for row in puzzle[:-1]:
        print("│" + "│".join(row) + "│")
        print("├" + "─┼" * (width - 1) + "─┤")
    print("│" + "│".join(puzzle[-1]) + "│")
    print("└" + "─┴" * (width - 1) + "─┘")


def parse_pynogram_file(puzzle_path):
    with open(puzzle_path) as f:
        lines = f.readlines()

    # Identify where the columns and rows start
    col_index = lines.index("columns =\n") + 1
    row_index = lines.index("rows =\n") + 1

    # Extract the column and row lines
    col_lines = lines[col_index : row_index - 2]
    row_lines = lines[row_index:]

    # Convert the lines to lists of clues
    column_clues = [
        list(map(int, line.split())) if line != "0" else [] for line in col_lines
    ]
    row_clues = [
        list(map(int, line.split())) if line != "0" else [] for line in row_lines
    ]

    return column_clues, row_clues

def are_2d_arrays_equal(array1, array2):
    rows = len(array1)
    cols = len(array1[0])

    for i in range(rows):
        for j in range(cols):
            if array1[i][j] != array2[i][j]:
                return False

    return True