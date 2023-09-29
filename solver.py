from collections.abc import Sequence
from utils import *
DEBUG = False

class Tile:
    """One tile in the puzzle. status may be space, X, or O."""

    def __init__(self):
        self.status = " "
        self.row_owner = None
        self.col_owner = None

    def __str__(self):
        return self.status

    def __eq__(self, value):
        return self.status == value

    def mark(self, new_status):
        self.status = new_status


class Line(Sequence):
    """A row or column bundled with its blocks and block domains.
    
    Block domains are inclusive ranges (start, end) that each block must be in.
    In the beginning of the solving process, many will overlap, representing ambiguity.
    We try to narrow these until they are the length of the block itself.

    has_changes generally represents progress being made on the puzzle solution.
    It is set to True whenever an X or an O is marked in this line,
    when one or more of this line's block domains are updated,
    and when one or more of this line's tiles have their block owners determined.
    """

    def __init__(self, is_row, position, tiles, blocks):
        self.is_row = is_row  # 'row' or 'col'.
        self.position = position
        self.tiles = tiles
        self.blocks = blocks
        self.block_domains = []
        self.has_changes = False

    def __getitem__(self, i):
        return self.tiles[i]

    def __len__(self):
        return len(self.tiles)

    def __contains__(self, value):
        return any(tile == value for tile in self)

    def __str__(self):
        return f"{'row' if self.is_row else 'col'} {self.position}"
    
    def get_owner_attr(self):
        return 'row_owner' if self.is_row else 'col_owner'

def fill_xs(line):
    for tile in line:
        tile.mark("X")
    line.has_changes = True
        
def get_tile_owner(line, tile_index):
    tile = line[tile_index]
    return getattr(tile, line.get_owner_attr())

def set_tile_owner(line, tile_index, block_index):
    tile = line[tile_index]
    setattr(tile, line.get_owner_attr(), block_index)
    

def set_up_tile_refs(height, width, row_clues, col_clues):
    """Returns a few different useful ways of indexing into/around the puzzle grid."""
    rows = []
    for row_index in range(height):
        row_tiles = [Tile() for _ in range(width)]
        row_blocks = row_clues[row_index]
        rows.append(Line(True, row_index, row_tiles, row_blocks))
    cols = []
    for col_index in range(width):
        col_tiles = [row[col_index] for row in rows]
        col_blocks = col_clues[col_index]
        cols.append(Line(False, col_index, col_tiles, col_blocks))

    return (rows, cols, rows + cols)


def init_block_domains(line):
    """Block by block, "slides" all other blocks to the edges of the grid.
    This gives us sort of a "worst case" baseline domain for the block to go in.
    """
    space_before = 0
    space_after = sum(line.blocks) + len(line.blocks)
    for block in line.blocks:
        space_after -= block + 1
        line.block_domains.append((space_before, len(line) - space_after - 1))
        space_before += block + 1

def fill_domain_centers(line):
    """Fills middle of domains where block is longer than half domain size."""
    # lines with hint array [0] have block_domains = [], skip those.
    if not line.block_domains: return

    for block_index, (block_len, block_domain) in enumerate(zip(line.blocks, line.block_domains)):
        domain_start, domain_end = block_domain
        domain_len = domain_end - domain_start + 1
        for i in range(domain_len - block_len, block_len):
            tile_index = domain_start + i
            tile = line[tile_index]
            if tile == "O":
                continue
            tile.mark("O")
            if DEBUG: print(f"FILD: setting {line} tile {tile_index} {line.get_owner_attr()} to block {block_index} [{line.blocks[block_index]}]")
            set_tile_owner(line, tile_index, block_index)
            line.has_changes = True


def get_active_domains(line, i):
    """hacky. quite redundant to do this for every tile in a line."""
    active_domains = []
    for domain_index, domain in enumerate(line.block_domains):
        a, b = domain
        if a <= i and i <= b:
            active_domains.append(domain_index)
    return active_domains

def identify_o_owners(line):
    """For Os with no recorded block owner across this axis (i.e. just placed),
    if only one block domain covers the O, that's the O's owner; mark it down.
    That information might allow us to constrain this and other domains down the line.
    """
    for tile_index, tile in enumerate(line):
        if tile != "O" or get_tile_owner(line, tile_index) != None:
            continue

        active_domains = get_active_domains(line, tile_index)
        assert len(active_domains) != 0 # Os should always belong to at least one domain
        # if several domains start or end at this O, we can tiebreak with left-right priority.
        if len(active_domains) > 1:
            active_domain_values = [line.block_domains[active_domain] for active_domain in active_domains]
            if all(domain[0] == tile_index for domain in active_domain_values):
                owner_block = active_domains[0]
            elif all(domain[1] == tile_index for domain in active_domain_values):
                owner_block = active_domains[-1]
            else: # still ambiguous
                continue
        else: # only one active domain
            owner_block = active_domains[0]
            
        if DEBUG:
            print(f"IOWN: setting {line} tile {tile_index} {line.get_owner_attr()} to block {owner_block} [{line.blocks[owner_block]}]")
        set_tile_owner(line, tile_index, owner_block)
        line.has_changes = True


def anchor_domains_around_os(line):
    """For every O in a line, if we know what block it belongs to,
    we can cut that block's domain to block_len away from that O."""
    for tile_index, tile in enumerate(line):
        owner_block = get_tile_owner(line, tile_index)
        if tile != "O" or owner_block is None:
            continue

        block_len = line.blocks[owner_block]
        block_domain = line.block_domains[owner_block]
        a, b = block_domain
        new_a = max(tile_index - block_len + 1, a)
        new_b = min(tile_index + block_len - 1, b)
        line.block_domains[owner_block] = (new_a, new_b)

def fill_no_domains_with_xs(line):
    """If there are no domains that cover a tile, that space must be empty."""
    for tile_index, tile in enumerate(line):
        if tile != " ":
            continue
        active_domains = get_active_domains(line, tile_index)
        if not active_domains:
            if DEBUG: print(f"FILX: setting {line} tile {tile_index} to X.")
            tile.mark("X")
            line.has_changes = True

def can_place_block_in_window(line, window_range, block):
    w_start, w_end = window_range
    window = line[w_start:w_end]
    for window_index, tile in enumerate(window):
        if tile == "X":
            return False
        elif tile == "O" and get_tile_owner(line, w_start + window_index) not in (block, None):
            return False
    return True

def constrain_domains_within_xs(line):
    """If there are some Xs at the edge of a block domain, slide that edge of the domain inward
    until there's no Xs preventing the block from going there.
    """
    for block_index, (block_len, block_domain) in enumerate(zip(line.blocks, line.block_domains)):
        a, b = block_domain
        while not can_place_block_in_window(line, (a, a + block_len), block_index):
            a += 1
            line.has_changes = True
        while not can_place_block_in_window(line, (b - block_len + 1, b + 1), block_index):
            b -= 1
            line.has_changes = True
        line.block_domains[block_index] = (a, b)
        if DEBUG and (a,b) != block_domain:
            print(f"SQSH: setting {line} block {block_index} [{block_len}] from {block_domain} to {(a,b)}")
            if a < 0:
                print("ERROR: domain underflow!")
            if b >= len(line):
                print("ERROR: domain overflow!")

def solve_puzzle(row_clues, col_clues):
    width, height = len(col_clues), len(row_clues)
    rows, cols, lines = set_up_tile_refs(height, width, row_clues, col_clues)

    for line in lines:
        if line.blocks[0] == 0:
            fill_xs(line)
            continue
        init_block_domains(line)
        fill_domain_centers(line)
    if DEBUG: print_puzzle(puzzle_to_2d_arr(rows))

    progress_made = True
    while progress_made:
        progress_made = False
        for line in lines: # lines includes rows, then columns.
            if DEBUG: print(f"Analyzing {line}...")
            #future optimization: check if line is complete and skip it
            identify_o_owners(line)
            anchor_domains_around_os(line) #if within a domain a block takes up enough that only it can be true, constrain to around
            fill_no_domains_with_xs(line)
            constrain_domains_within_xs(line) #consider: constrain domains within xs and blocks known to be owned by neighbors

            fill_domain_centers(line)
            if line.has_changes:
                if DEBUG: print_puzzle(puzzle_to_2d_arr(rows))
                progress_made = True
                line.has_changes = False # reset for next iteration

    if DEBUG:
        print_unfinished_line_domains(lines)
        print_block_owners(rows)
    return puzzle_to_2d_arr(rows)

def print_block_owners(rows):
    for line in rows:
        for tile_index, tile in enumerate(line):
            if tile == "O" and (tile.row_owner == None or tile.col_owner == None):
                print(f"{line} tile at {tile_index} owned by row block {tile.row_owner}, col block {tile.col_owner}")

def print_unfinished_line_domains(lines):
    for line in lines:
        if ' ' in line:
            domains_str = [f"[{block}] {block_domain}" for block, block_domain in zip(line.blocks, line.block_domains)]
            print(f"{line} unfinished, domains:\n{', '.join(domains_str)}\n")

if __name__ == "__main__":
    debug_puzzle = "39883"
    column_clues, row_clues = parse_pynogram_file(f"data/puzzles/{debug_puzzle}.txt")

    print(f"Solving test puzzle {debug_puzzle}...")
    our_solution = solve_puzzle(row_clues, column_clues)

    # print("Expected:")
    # print_puzzle(puzzle["solution"])
    print("Got:")
    print_puzzle(our_solution)

