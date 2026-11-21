"""main.py - PR2 text prototype for Game of Life with Music.

Only reads input and prints. All logic lives in life.py, patterns.py and
music.py (music is optional and skipped if not ready).

Usage:
    python main.py                      # Blinker, 5x5 board, 10 generations
    python main.py glider 8 8 12        # pattern, rows, cols, max generations
"""
import sys

import life
import patterns

PATTERN_NAMES = {"block": "Block", "blinker": "Blinker", "glider": "Glider"}


def get_pattern_cells(name):
    """Return the list of (row, col) cells for a pattern name."""
    key = name.strip().lower()
    if key not in PATTERN_NAMES:
        raise ValueError("Unknown pattern '%s'. Choose: block, blinker, glider." % name)
    for attr in (PATTERN_NAMES[key], key.upper(), key):
        if hasattr(patterns, attr):
            return list(getattr(patterns, attr))
    raise ValueError("patterns.py has no pattern called '%s'." % name)


def build_start_grid(name, rows, cols):
    grid = life.create_grid(rows, cols)
    cells = get_pattern_cells(name)
    # Place the pattern one cell in from the top-left corner.
    for r, c in cells:
        rr, cc = r + 1, c + 1
        if not (0 <= rr < rows and 0 <= cc < cols):
            raise ValueError("Board %dx%d is too small for the %s." % (rows, cols, name))
        grid[rr][cc] = 1
    return grid


def format_grid(grid):
    return "\n".join("".join("#" if cell else "." for cell in row) for row in grid)


def is_empty(grid):
    return all(cell == 0 for row in grid for cell in row)


def describe_music(old, new):
    """Optional: show notes chosen for this generation, if music.py is ready."""
    try:
        import music
        births, deaths = life.compare_generations(old, new)
        notes = music.map_generation_to_notes(births, deaths, new)
        return "Notes: " + str(music.describe_notes(notes))
    except Exception:
        return None


def run(name, rows, cols, max_gens, show_music=False):
    grid = build_start_grid(name, rows, cols)
    print("Pattern: %s  Board: %dx%d  Max generations: %d" % (name, rows, cols, max_gens))
    print("\nGeneration 0")
    print(format_grid(grid))
    for gen in range(1, max_gens + 1):
        new = life.next_generation(grid)
        print("\nGeneration %d" % gen)
        print(format_grid(new))
        if show_music:
            line = describe_music(grid, new)
            if line:
                print(line)
        if is_empty(new):
            print("\nStopped: board is empty at generation %d." % gen)
            return
        if new == grid:
            print("\nStopped: stable (no change) at generation %d." % gen)
            return
        grid = new
    print("\nStopped: reached %d generations." % max_gens)


def main(argv):
    name = argv[1] if len(argv) > 1 else "blinker"
    try:
        rows = int(argv[2]) if len(argv) > 2 else 5
        cols = int(argv[3]) if len(argv) > 3 else 5
        gens = int(argv[4]) if len(argv) > 4 else 10
        run(name, rows, cols, gens, show_music="--music" in argv)
    except ValueError as err:
        print("Error: %s" % err)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
