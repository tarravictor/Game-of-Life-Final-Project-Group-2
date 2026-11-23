"""Core Conway's Game of Life logic."""

def create_grid(rows, cols):
    """Create a rectangular grid filled with dead cells (0)."""
    if not isinstance(rows, int) or not isinstance(cols, int):
        raise TypeError("rows and cols must be integers")
    if rows <= 0 or cols <= 0:
        raise ValueError("rows and cols must be positive")
    return [[0 for _ in range(cols)] for _ in range(rows)]


def validate_grid(grid):
    """Return True when grid is rectangular and contains only 0/1 values."""
    if not isinstance(grid, list) or not grid:
        return False
    if not all(isinstance(row, list) for row in grid):
        return False
    width = len(grid[0])
    if width == 0 or any(len(row) != width for row in grid):
        return False
    return all(cell in (0, 1) for row in grid for cell in row)


def copy_grid(grid):
    """Make a separate copy so changes cannot affect the original."""
    return [row[:] for row in grid]


def in_bounds(grid, row, col):
    """Check whether a coordinate is inside the board."""
    return 0 <= row < len(grid) and 0 <= col < len(grid[0])


def population(grid):
    """Count live cells."""
    return sum(sum(row) for row in grid)


def count_live_neighbors(grid, row, col):
    """Count live neighbors around a cell; off-board positions are dead."""
    total = 0
    rows, cols = len(grid), len(grid[0])
    for r in range(row - 1, row + 2):
        for c in range(col - 1, col + 2):
            if (r, c) == (row, col):
                continue
            if 0 <= r < rows and 0 <= c < cols:
                total += grid[r][c]
    return total


def next_cell_state(cell, neighbors):
    """Apply Conway's B3/S23 rule to one cell."""
    if neighbors == 3:
        return 1
    if cell == 1 and neighbors == 2:
        return 1
    return 0


def next_generation(grid):
    """Calculate the next board using a new grid and a row/column loop."""
    if not validate_grid(grid):
        raise ValueError("grid must be a non-empty rectangular list of 0/1 rows")
    rows, cols = len(grid), len(grid[0])
    new_grid = create_grid(rows, cols)
    for row in range(rows):
        for col in range(cols):
            neighbors = count_live_neighbors(grid, row, col)
            new_grid[row][col] = next_cell_state(grid[row][col], neighbors)
    return new_grid


def compare_generations(previous, current):
    """Return (births, deaths) between two boards as lists of (row, col).

    A birth is a cell that was 0 and is now 1; a death is 1 -> 0.
    state.py and music.py use these to pick the notes for each generation.
    """
    births, deaths = [], []
    for row in range(len(current)):
        for col in range(len(current[0])):
            before, after = previous[row][col], current[row][col]
            if before == 0 and after == 1:
                births.append((row, col))
            elif before == 1 and after == 0:
                deaths.append((row, col))
    return births, deaths


def same_board(previous, current):
    """True when two boards have identical cell states (still life)."""
    return previous == current


def simulate(grid, max_generations=1000):
    """Run until empty, stable, or max_generations; return board, reason, count."""
    if not validate_grid(grid):
        raise ValueError("grid must be a non-empty rectangular list of 0/1 rows")
    current = copy_grid(grid)
    if population(current) == 0:
        return current, "empty", 0
    for generation in range(1, max_generations + 1):
        new_grid = next_generation(current)
        if population(new_grid) == 0:
            return new_grid, "empty", generation
        if same_board(current, new_grid):
            return new_grid, "stable", generation
        current = new_grid
    return current, "limit", max_generations


if __name__ == "__main__":
    sample = create_grid(10, 10)
    sample[4][4:7] = [1, 1, 1]  # horizontal blinker
    final_grid, reason, steps = simulate(sample, max_generations=20)
    print(f"Stopped: {reason} after {steps} generation(s)")
    for row in final_grid:
        print("".join(str(cell) for cell in row))
