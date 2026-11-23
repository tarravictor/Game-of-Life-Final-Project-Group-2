"""Tests for gui.py helpers (no window needed).  Owner: Tarra"""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import gui
import patterns
from state import State


class TestGuiHelpers(unittest.TestCase):
    def test_click_inside_grid_gives_row_and_col(self):
        self.assertEqual(gui.cell_at((gui.GRID_X + gui.CELL + 1, gui.GRID_Y + 2 * gui.CELL + 1)), (2, 1))

    def test_click_outside_grid_is_ignored(self):
        self.assertIsNone(gui.cell_at((0, 0)))
        self.assertIsNone(gui.cell_at((gui.GRID_X + gui.GRID_W, gui.GRID_Y)))

    def test_pattern_is_centered_and_board_cleared(self):
        state = State(gui.ROWS, gui.COLS)
        state.toggle_cell(0, 0)
        gui.place_centered(state, patterns.BLOCK)
        self.assertEqual(state.count_living(), 4)
        self.assertEqual(state.grid[0][0], 0)
        self.assertEqual(state.grid[gui.ROWS // 2 - 1][gui.COLS // 2 - 1], 1)

    def test_faster_speed_means_more_steps(self):
        self.assertLess(gui.steps_per_second(1), gui.steps_per_second(10))


if __name__ == "__main__":
    unittest.main()
