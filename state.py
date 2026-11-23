import random

import life


class State:
    def __init__(self, rows=20, cols=20):
        self.grid = life.create_grid(rows, cols)
        self.previous = None
        self.generation = 0
        self.playing = False
        self.stopped = False
        self.stop_reason = ""
        self.speed = 5

    def step_once(self):
        # move one generation forward, nothing is drawn here
        old = self.grid
        new = life.next_generation(old)
        self.previous = old
        self.grid = new
        self.generation += 1

        # stop when the board is empty or did not change (still life)
        if self.is_empty():
            self.playing = False
            self.stopped = True
            self.stop_reason = "empty"
        elif new == old:
            self.playing = False
            self.stopped = True
            self.stop_reason = "stable"
        return new

    def changes(self):
        # births and deaths of the last step, music.py uses these
        if self.previous is None:
            return [], []
        return life.compare_generations(self.previous, self.grid)

    def count_living(self):
        total = 0
        for row in self.grid:
            for cell in row:
                if cell == 1:
                    total += 1
        return total

    def is_empty(self):
        return self.count_living() == 0

    def toggle_play(self):
        self.playing = not self.playing
        if self.playing:
            self.stopped = False
            self.stop_reason = ""

    def clear(self):
        rows = len(self.grid)
        cols = len(self.grid[0])
        self.grid = life.create_grid(rows, cols)
        self.previous = None
        self.generation = 0
        self.playing = False
        self.stopped = False
        self.stop_reason = ""

    def randomize(self):
        # about 25% of the cells start alive
        self.clear()
        for r in range(len(self.grid)):
            for c in range(len(self.grid[0])):
                if random.random() < 0.25:
                    self.grid[r][c] = 1

    def set_speed(self, speed):
        # keep speed between 1 and 10
        if speed < 1:
            speed = 1
        if speed > 10:
            speed = 10
        self.speed = speed

    def toggle_cell(self, row, col):
        if row < 0 or row >= len(self.grid):
            return
        if col < 0 or col >= len(self.grid[0]):
            return
        if self.grid[row][col] == 1:
            self.grid[row][col] = 0
        else:
            self.grid[row][col] = 1
