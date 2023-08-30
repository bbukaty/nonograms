from collections.abc import Sequence
import json


class Tile:
    """One tile in the puzzle. status may be space, X, or O."""

    def __init__(self):
        self.status = " "
        self.isFresh = False

    def __str__(self):
        return self.status

    def set(self, newStatus):
        self.status = newStatus


class Line(Sequence):
    """A row or column bundled with its blocks and block domains.
    Block domains are inclusive ranges (start, end) that each block must be in.
    We try to narrow these until they are the length of the block itself.
    """

    def __init__(self, tiles, blocks):
        self.tiles = tiles
        self.blocks = blocks
        self.blockDomains = []

    def __getitem__(self, i):
        return self.tiles[i]

    def __len__(self):
        return len(self.tiles)

    def __str__(self) -> str:
        return "".join([str(tile) for tile in self.tiles])

    def fillXs(self):
        for tile in self:
            tile.set("X")

def printPuzzle(puzzle):
    """Takes 2d arr of strings, prints nonogram in ascii.
    TODO print hints above and beside puzzle
    """
    width = len(puzzle[0])
    print("┌" + "─┬" * (width-1) + "─┐")
    for row in puzzle[:-1]:
        print("│" + "│".join(row) + "│")
        print("├" + "─┼" * (width-1) + "─┤")
    print("│" + "│".join(puzzle[-1]) + "│")
    print("└" + "─┴" * (width-1) + "─┘")

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
    """Fills middle of block domains based on simple "sliding" heuristic."""
    if not line.blockDomains: return

    for i in range(len(line.blocks)):
        blockLen, blockDomain = line.blocks[i], line.blockDomains[i]
        domainStart, domainEnd = blockDomain
        domainLen = domainEnd - domainStart + 1
        if 2 * blockLen > domainLen:
            line.hasNewTiles = True
        for i in range(domainLen - blockLen, blockLen):
            line[domainStart + i].status = "O"


def setUpTileRefs(height, width, rowHints, colHints):
    """Returns a few different useful ways of indexing into the puzzle grid."""
    rows = []
    for row in range(height):
        rowTiles = [Tile() for _ in range(width)]
        rowBlocks = rowHints[row]
        rows.append(Line(rowTiles, rowBlocks))
    cols = []
    for col in range(width):
        colTiles = [row[col] for row in rows]
        colBlocks = colHints[col]
        cols.append(Line(colTiles, colBlocks))
    return (rows, cols, rows + cols)


def getActiveDomains(line, i):
    """hacky. not ideal to do this for every tile in a line."""
    activeDomains = []
    for domainIndex, domain in enumerate(line.blockDomains):
        a, b = domain
        if a <= i or i <= b:
            activeDomains.append(domainIndex)
    return activeDomains

def anchorDomainsAroundOs(line):
    """Find O tiles; domain has to end <block> away from them, use this to cut"""
    for i, tile in enumerate(line):
        if tile.status != "O":
            continue
        activeDomains = line.getActiveDomains()

        assert len(activeDomains) > 0  # every O should have >=1 domains
        if len(activeDomains) == 1:
            blockIndex = activeDomains[0]
            blockLen = line.blocks[blockIndex]
            currDomain = line.blockDomains[blockIndex]
            a, b = currDomain
            newA = max(i - blockLen + 1, a)
            newB = min(i + blockLen - 1, b)
            print(f"updating blockDomain from ({a},{b}) ({newA},{newB})")
            line.blockDomains[blockIndex] = (newA, newB)


def solvePuzzle(height, width, rowHints, colHints):
    assert len(rowHints) == height and len(colHints) == width
    rows, cols, lines = setUpTileRefs(height, width, rowHints, colHints)

    for line in lines:
        initBlockDomains(line)
        fillDomainCenters(line)
    
    return [[str(tile) for tile in row] for row in rows]


if __name__ == "__main__":
    debugPuzzle = "5x5_1"
    with open(f"puzzles/{debugPuzzle}.json") as f:
        puzzle = json.load(f)
        height, width = puzzle["size"]
        print(f"Solving test puzzle {debugPuzzle}...")
        ourSolution = solvePuzzle(
            height, width, puzzle["rowHints"], puzzle["colHints"])

        print("Expected:")
        printPuzzle(puzzle["solution"])
        print("Got:")
        printPuzzle(ourSolution)
