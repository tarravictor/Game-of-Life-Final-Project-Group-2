"""Common Game of Life patterns and a helper for placing them."""

BLOCK = [(0, 0), (0, 1), (1, 0), (1, 1)]
BLINKER = [(0, 0), (0, 1), (0, 2)]
GLIDER = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]


def place_pattern(grid, pattern, top=0, left=0):
    """Place live cells of pattern at offset (top, left), modifying grid.

    Cells that would fall outside the board are ignored. Returns the grid.
    """
    for row_offset, col_offset in pattern:
        row, col = top + row_offset, left + col_offset
        if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
            grid[row][col] = 1
    return grid
