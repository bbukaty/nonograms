from collections.abc import Sequence
from utils import *
DEBUG = False

class Tile:
    """One tile in the puzzle. status may be space, X, or O."""

    def __init__(self):
        self.status = " "
        self.row = None
        self.col = None

    def __str__(self):
        return self.status

    def __eq__(self, __value):
        return self.status == __value

    def set(self, newStatus):
        self.status = newStatus


class Line(Sequence):
    """A row or column bundled with its blocks and block domains.
    Block domains are inclusive ranges (start, end) that each block must be in.
    We try to narrow these until they are the length of the block itself.
    """

    def __init__(self, orientation, position, tiles, blocks):
        self.orientation = orientation  # 'row' or 'col'.
        self.position = position
        self.tiles = tiles
        self.blocks = blocks
        self.blockDomains = []
        self.hasChanges = False

    def __getitem__(self, i):
        return self.tiles[i]

    def __len__(self):
        return len(self.tiles)

    def __contains__(self, value):
        for tile in self:
            if tile.status == value: return True
        return False

    def __str__(self):
        return f"{self.orientation} {self.position}"

    def fillXs(self):
        for tile in self:
            tile.set("X")
        self.hasChanges = True


def setUpTileRefs(height, width, row_clues, col_clues):
    """Returns a few different useful ways of indexing into/around the puzzle grid."""
    rows = []
    for rowIndex in range(height):
        rowTiles = [Tile() for _ in range(width)]
        rowBlocks = row_clues[rowIndex]
        rows.append(Line("row", rowIndex, rowTiles, rowBlocks))
    cols = []
    for colIndex in range(width):
        colTiles = [row[colIndex] for row in rows]
        colBlocks = col_clues[colIndex]
        cols.append(Line("col", colIndex, colTiles, colBlocks))

    for rowIndex in range(height):
        for colIndex in range(width):
            tile = rows[rowIndex][colIndex]
            tile.row = rows[rowIndex]
            tile.col = cols[colIndex]
    return (rows, cols, rows + cols)


def initBlockDomains(line):
    """Block by block, "slides" all other blocks to the edges of the grid.
    This gives us sort of a "worst case" baseline domain for the block to go in.
    """
    spaceBefore = 0
    spaceAfter = sum(line.blocks) + len(line.blocks)
    for block in line.blocks:
        spaceAfter -= block + 1
        line.blockDomains.append((spaceBefore, len(line) - spaceAfter - 1))
        spaceBefore += block + 1

def fillDomainCenters(line):
    """Fills middle of domains where block is longer than half domain size."""
    if not line.blockDomains: return

    for i in range(len(line.blockDomains)):
        blockLen, blockDomain = line.blocks[i], line.blockDomains[i]
        domainStart, domainEnd = blockDomain
        domainLen = domainEnd - domainStart + 1
        for i in range(domainLen - blockLen, blockLen):
            lineIndex = domainStart + i
            if line[lineIndex].status == "O":
                continue
            line[lineIndex].status = "O"
            if DEBUG: print(f"added an O at index {lineIndex}")
            line.hasChanges = True


def getActiveDomains(line, i):
    """hacky. quite redundant to do this for every tile in a line."""
    activeDomains = []
    for domainIndex, domain in enumerate(line.blockDomains):
        a, b = domain
        if a <= i and i <= b:
            activeDomains.append(domainIndex)
    return activeDomains

def anchorDomainsAroundOs(line):
    """For every O in a line, if we know what block it belongs to,
    we can cut that block's domain to blockLen away from that O."""
    for tileIndex, tile in enumerate(line):
        if tile.status != "O":
            continue
        activeDomains = getActiveDomains(line, tileIndex)

        assert len(activeDomains) > 0  # every O should have >=1 domains
        if len(activeDomains) == 1:
            blockIndex = activeDomains[0]
            blockLen = line.blocks[blockIndex]
            currDomain = line.blockDomains[blockIndex]
            a, b = currDomain
            newA = max(tileIndex - blockLen + 1, a)
            newB = min(tileIndex + blockLen - 1, b)
            line.blockDomains[blockIndex] = (newA, newB)

def fillNoDomainsWithXs(line):
    """If there are no domains that cover an index in a line, that space must be empty; put an X there."""
    for i, tile in enumerate(line):
        if tile.status != " ":
            continue
        activeDomains = getActiveDomains(line, i)
        if not activeDomains:
            if DEBUG: print(f"added an X at index {i}")
            tile.status = "X"
            line.hasChanges = True

def constrainDomainsWithinXs(line):
    """If there are some Xs at the edge of a block domain, slide that edge of the domain inward
    until there's no Xs preventing the block from going there.
    """
    for blockIndex, (blockLen, blockDomain) in enumerate(zip(line.blocks, line.blockDomains)):
        a, b = blockDomain
        while "X" in line[a:a+blockLen]:
            a += 1
        while "X" in line[b-blockLen+1:b+1]:
            b -= 1
        line.blockDomains[blockIndex] = (a, b)

def solvePuzzle(row_clues, col_clues):
    width, height = len(col_clues), len(row_clues)
    rows, cols, lines = setUpTileRefs(height, width, row_clues, col_clues)

    for line in lines:
        if DEBUG: print(f"{line}")
        if line.blocks[0] == 0:
            line.fillXs()
            continue
        initBlockDomains(line)
        fillDomainCenters(line)

    progressMade = True
    while progressMade:
        progressMade = False
        for line in lines: # lines includes rows, then columns.
            #future optimization: check if line is complete and skip it
            if DEBUG: print(f"{line}")
            anchorDomainsAroundOs(line)
            fillNoDomainsWithXs(line)
            constrainDomainsWithinXs(line)
            fillDomainCenters(line)
            if line.hasChanges:
                progressMade = True
                line.hasChanges = False # reset for next iteration

    return [[str(tile) for tile in row] for row in rows]


if __name__ == "__main__":
    debugPuzzle = "13698"
    column_clues, row_clues = parse_pynogram_file(f"data/puzzles/{debugPuzzle}.txt")

    print(f"Solving test puzzle {debugPuzzle}...")
    ourSolution = solvePuzzle(row_clues, column_clues)

    # print("Expected:")
    # print_puzzle(puzzle["solution"])
    print("Got:")
    print_puzzle(ourSolution)
