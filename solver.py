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

    def set(self, new_status):
        self.status = new_status


class Line(Sequence):
    """A row or column bundled with its blocks and block domains.
    Block domains are inclusive ranges (start, end) that each block must be in.
    We try to narrow these until they are the length of the block itself.
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
        for tile in self:
            if tile == value: return True
        return False

    def __str__(self):
        return f"{'row' if self.is_row else 'col'} {self.position}"

    def fill_xs(self):
        for tile in self:
            tile.set("X")
        self.has_changes = True


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
    if not line.block_domains: return

    for block_index, (block_len, block_domain) in enumerate(zip(line.blocks, line.block_domains)):
        domain_start, domain_end = block_domain
        domain_len = domain_end - domain_start + 1
        for i in range(domain_len - block_len, block_len):
            tile_index = domain_start + i
            tile = line[tile_index]

            # in this context we know the owner of the current tile, mark it if that's new info
            attribute = 'row_owner' if line.is_row else 'col_owner'
            if getattr(tile, attribute) is None:
                setattr(tile, attribute, block_index)
                line.has_changes = True

            if tile == "O":
                continue
            tile.status = "O"
            line.has_changes = True
                
            if DEBUG: print(f"{line}: added an O at index {tile_index}")


def get_active_domains(line, i):
    """hacky. quite redundant to do this for every tile in a line."""
    active_domains = []
    for domain_index, domain in enumerate(line.block_domains):
        a, b = domain
        if a <= i and i <= b:
            active_domains.append(domain_index)
    return active_domains

def anchor_domains_around_os(line):
    """For every O in a line, if we know what block it belongs to,
    we can cut that block's domain to block_len away from that O."""
    for tile_index, tile in enumerate(line):
        if tile != "O":
            continue
        block_index = getattr(tile, 'row_owner' if line.is_row else 'col_owner')
        if block_index is None:
            active_domains = get_active_domains(line, tile_index)
            assert len(active_domains) != 0 # Os should always have at least one, maybe more.
            if len(active_domains) > 1:
                continue
            block_index = active_domains[0]

        block_len = line.blocks[block_index]
        curr_domain = line.block_domains[block_index]
        a, b = curr_domain
        new_a = max(tile_index - block_len + 1, a)
        new_b = min(tile_index + block_len - 1, b)
        line.block_domains[block_index] = (new_a, new_b)

def fill_no_domains_with_xs(line):
    """If there are no domains that cover an index in a line, that space must be empty; put an X there."""
    for i, tile in enumerate(line):
        if tile.status != " ":
            continue
        active_domains = get_active_domains(line, i)
        if not active_domains:
            if DEBUG: print(f"{line}: added an X at index {i}")
            tile.status = "X"
            line.has_changes = True

def constrain_domains_within_xs(line):
    """If there are some Xs at the edge of a block domain, slide that edge of the domain inward
    until there's no Xs preventing the block from going there.
    """
    for block_index, (block_len, block_domain) in enumerate(zip(line.blocks, line.block_domains)):
        a, b = block_domain
        # while cantPlaceInWindow, a+=1? include logic for neighbor-owned blocks
        while "X" in line[a:a+block_len]:
            a += 1
        while "X" in line[b-block_len+1:b+1]:
            b -= 1
        line.block_domains[block_index] = (a, b)

def solve_puzzle(row_clues, col_clues):
    width, height = len(col_clues), len(row_clues)
    rows, cols, lines = set_up_tile_refs(height, width, row_clues, col_clues)

    for line in lines:
        if line.blocks[0] == 0:
            line.fill_xs()
            continue
        init_block_domains(line)
        fill_domain_centers(line)

    progress_made = True
    while progress_made:
        progress_made = False
        for line in lines: # lines includes rows, then columns.
            #future optimization: check if line is complete and skip it

            anchor_domains_around_os(line) #if within a domain a block takes up enough that only it can be true, constrain to around
            fill_no_domains_with_xs(line)
            constrain_domains_within_xs(line) #consider: constrain domains within xs and blocks known to be owned by neighbors

            fill_domain_centers(line)
            if line.has_changes:
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
    debug_puzzle = "13918"
    column_clues, row_clues = parse_pynogram_file(f"data/puzzles/{debug_puzzle}.txt")

    print(f"Solving test puzzle {debug_puzzle}...")
    our_solution = solve_puzzle(row_clues, column_clues)

    # print("Expected:")
    # print_puzzle(puzzle["solution"])
    print("Got:")
    print_puzzle(our_solution)

