import unittest

import life
import state


def make_grid(cells, size=20):
    # build a grid with 1s at the given (row, col) cells
    grid = life.create_grid(size, size)
    for r, c in cells:
        grid[r][c] = 1
    return grid


def live_cells(grid):
    cells = []
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 1:
                cells.append((r, c))
    return cells


def run(grid, generations):
    for i in range(generations):
        grid = life.next_generation(grid)
    return grid


class TestNormalCases(unittest.TestCase):
    def test_block_stays_the_same(self):
        block = [(5, 5), (5, 6), (6, 5), (6, 6)]
        grid = make_grid(block)
        result = life.next_generation(grid)
        self.assertEqual(sorted(live_cells(result)), sorted(block))

    def test_blinker_flips_every_generation(self):
        horizontal = [(5, 4), (5, 5), (5, 6)]
        vertical = [(4, 5), (5, 5), (6, 5)]
        grid = make_grid(horizontal)
        gen1 = life.next_generation(grid)
        self.assertEqual(sorted(live_cells(gen1)), sorted(vertical))
        gen2 = life.next_generation(gen1)
        self.assertEqual(sorted(live_cells(gen2)), sorted(horizontal))

    def test_glider_moves_diagonally_after_4_generations(self):
        glider = [(1, 2), (2, 3), (3, 1), (3, 2), (3, 3)]
        grid = make_grid(glider)
        result = run(grid, 4)
        moved = []
        for r, c in glider:
            moved.append((r + 1, c + 1))
        self.assertEqual(sorted(live_cells(result)), sorted(moved))


class TestBoundaryCase(unittest.TestCase):
    def test_blinker_on_top_row(self):
        # cells above the board count as dead
        grid = make_grid([(0, 5), (0, 6), (0, 7)])
        result = life.next_generation(grid)
        self.assertEqual(sorted(live_cells(result)), [(0, 6), (1, 6)])


class TestInvalidInput(unittest.TestCase):
    def test_grid_with_a_2_in_it(self):
        grid = life.create_grid(20, 20)
        grid[3][3] = 2
        with self.assertRaises(ValueError):
            life.next_generation(grid)


class TestState(unittest.TestCase):
    def test_toggle_cell(self):
        s = state.State()
        s.toggle_cell(2, 2)
        self.assertEqual(s.grid[2][2], 1)
        s.toggle_cell(2, 2)
        self.assertEqual(s.grid[2][2], 0)

    def test_step_once_stops_when_empty(self):
        s = state.State()
        s.playing = True
        s.step_once()
        self.assertTrue(s.stopped)
        self.assertFalse(s.playing)
        self.assertEqual(s.stop_reason, "empty")

    def test_step_once_stops_on_still_life(self):
        s = state.State()
        for r, c in [(5, 5), (5, 6), (6, 5), (6, 6)]:
            s.toggle_cell(r, c)
        s.playing = True
        s.step_once()
        self.assertTrue(s.stopped)
        self.assertEqual(s.stop_reason, "stable")
        self.assertEqual(s.generation, 1)

    def test_blinker_does_not_stop(self):
        s = state.State()
        for r, c in [(5, 4), (5, 5), (5, 6)]:
            s.toggle_cell(r, c)
        s.playing = True
        s.step_once()
        self.assertFalse(s.stopped)
        self.assertTrue(s.playing)

    def test_changes_gives_births_and_deaths(self):
        s = state.State()
        for r, c in [(5, 4), (5, 5), (5, 6)]:
            s.toggle_cell(r, c)
        s.step_once()
        births, deaths = s.changes()
        self.assertEqual(sorted(births), [(4, 5), (6, 5)])
        self.assertEqual(sorted(deaths), [(5, 4), (5, 6)])


if __name__ == "__main__":
    unittest.main()
