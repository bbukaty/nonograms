from collections.abc import Sequence
from utils import *

class Tile:
    """One tile in the puzzle. status may be space, X, or O."""

    def __init__(self):
        self.status = " "
        self.row = None
        self.col = None

    def __str__(self):
        return self.status

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
    """Block by block, "slides" all other blocks out of the way to determine
    the full area that block could be placed in.
    """
    if line.blocks[0] == 0:
        line.fillXs()
        return []
    spaceBefore = 0
    spaceAfter = sum(line.blocks) + len(line.blocks)
    for block in line.blocks:
        spaceAfter -= block + 1
        line.blockDomains.append((spaceBefore, len(line) - spaceAfter - 1))
        spaceBefore += block + 1

def fillDomainCenters(line):
    """Fills middle of domains where block is longer than half domain size."""
    if not line.blockDomains: return []

    for i in range(len(line.blockDomains)):
        blockLen, blockDomain = line.blocks[i], line.blockDomains[i]
        domainStart, domainEnd = blockDomain
        domainLen = domainEnd - domainStart + 1
        for i in range(domainLen - blockLen, blockLen):
            line[domainStart + i].status = "O"


def getActiveDomains(line, i):
    """hacky. not ideal to do this for every tile in a line."""
    activeDomains = []
    for domainIndex, domain in enumerate(line.blockDomains):
        a, b = domain
        if a <= i and i <= b:
            activeDomains.append(domainIndex)
    return activeDomains

def anchorDomainsAroundOs(line):
    """Find O tiles; domain has to end <block> away from them, use this to cut"""
    for i, tile in enumerate(line):
        if tile.status != "O":
            continue
        activeDomains = getActiveDomains(line, i)

        assert len(activeDomains) > 0  # every O should have >=1 domains
        if len(activeDomains) == 1:
            blockIndex = activeDomains[0]
            blockLen = line.blocks[blockIndex]
            currDomain = line.blockDomains[blockIndex]
            a, b = currDomain
            newA = max(i - blockLen + 1, a)
            newB = min(i + blockLen - 1, b)
            line.blockDomains[blockIndex] = (newA, newB)

def fillNoDomainsWithXs(line):
    """Sweep a line for regions with no active domains. Fill with Xs."""
    for i, tile in enumerate(line):
        if tile.status != " ":
            continue
        activeDomains = getActiveDomains(line, i)

        if not activeDomains:
            tile.status = "X"

def constrainDomainsWithinXs(line):
    for i in range(len(line.blockDomains)):
        blockLen, blockDomain = line.blocks[i], line.blockDomains[i]
        domainStart, domainEnd = blockDomain
        while "X" in [tile.status for tile in line[domainStart:domainStart+blockLen]]:
            domainStart += 1
        while "X" in [tile.status for tile in line[domainEnd-blockLen+1:domainEnd+1]]:
            domainEnd -= 1
        line.blockDomains[i] = (domainStart, domainEnd)
        # while "X" in line

def solvePuzzle(row_clues, col_clues):
    width, height = len(col_clues), len(row_clues)
    rows, cols, lines = setUpTileRefs(height, width, row_clues, col_clues)

    for line in lines:
        initBlockDomains(line)
        fillDomainCenters(line)

    for _ in range(2):
        for line in lines:
            anchorDomainsAroundOs(line)
        for line in lines:
            pass
        for line in lines:
            fillNoDomainsWithXs(line)
            constrainDomainsWithinXs(line)
        for line in lines:
            fillDomainCenters(line)

    return [[str(tile) for tile in row] for row in rows]


if __name__ == "__main__":
    debugPuzzle = "57596"
    column_clues, row_clues = parse_pynogram_file(f"data/puzzles/{debugPuzzle}.txt")

    print(f"Solving test puzzle {debugPuzzle}...")
    ourSolution = solvePuzzle(row_clues, column_clues)

    # print("Expected:")
    # print_puzzle(puzzle["solution"])
    print("Got:")
    print_puzzle(ourSolution)
