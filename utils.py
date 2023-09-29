def print_puzzle_ascii(puzzle):
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

def puzzle_row_to_emoji(row):
    line = ''
    for cell in row:
        if cell == ' ':
            line += '🟧'  # Two spaces for consistent width with emojis
        elif cell == 'O':
            line += '⬛'
        elif cell == 'X':
            line += '⬜'
        else:
            line += '❓'
    return line

def print_puzzle(puzzle):
    for row in puzzle:
        print(puzzle_row_to_emoji(row))
    print()

def puzzle_to_2d_arr(puzzle_rows):
    return [[str(tile) for tile in row] for row in puzzle_rows]

def animate_solve(puzzle_rows):
    print_puzzle(puzzle_to_2d_arr(puzzle_rows))
    print("\033c", end='')
    print("\033[H", end='')

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