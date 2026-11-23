"""gui.py - pygame window for Game of Life with Music.  Owner: Tarra

Layout follows the PR1 wireframe: the grid on the left, a side panel with
the controls on the right, and a status bar along the bottom.

The rules live in life.py and the controls' logic in state.py; this file only
draws and reads the mouse and keyboard.

Run:  python gui.py
Keys: Space play/pause, S step, C clear, R random, M mute,
      1 block, 2 blinker, 3 glider, Up/Down speed
"""

import sys

import pygame

import music
import patterns
import sound
from state import State

# ---- sizes -------------------------------------------------------------
ROWS, COLS = 30, 40
CELL = 18
MARGIN = 20
TITLE_H = 56
STATUS_H = 48
PANEL_W = 300

GRID_X = MARGIN
GRID_Y = TITLE_H + MARGIN
GRID_W = COLS * CELL
GRID_H = ROWS * CELL
PANEL_X = GRID_X + GRID_W + MARGIN
WIDTH = PANEL_X + PANEL_W + MARGIN
HEIGHT = GRID_Y + GRID_H + MARGIN + STATUS_H + MARGIN

# ---- colours (same palette as our PR slides) ---------------------------
PAPER = (242, 237, 228)
PANEL = (231, 224, 212)
LINE = (207, 198, 182)
INK = (28, 27, 25)
MUTED = (140, 135, 125)
ACCENT = (228, 87, 46)
WHITE = (255, 255, 255)
BIRTH = (228, 87, 46)

PATTERNS = {"Block": patterns.BLOCK, "Blinker": patterns.BLINKER, "Glider": patterns.GLIDER}
INSTRUMENTS = list(sound.INSTRUMENTS)          # Piano, Organ, Bell
SCALE = next(iter(music.SCALES))


# ---- small helpers (no drawing, easy to test) --------------------------
def cell_at(pos):
    """Mouse position -> (row, col) on the grid, or None if outside it."""
    x, y = pos
    if not (GRID_X <= x < GRID_X + GRID_W and GRID_Y <= y < GRID_Y + GRID_H):
        return None
    return (y - GRID_Y) // CELL, (x - GRID_X) // CELL


def steps_per_second(speed):
    """Speed 1..10 -> generations per second (1 is slow, 10 is fast)."""
    return speed * 1.5


def place_centered(state, cells):
    """Clear the board and put a pattern in the middle."""
    state.clear()
    height = max(r for r, c in cells) + 1
    width = max(c for r, c in cells) + 1
    top = (ROWS - height) // 2
    left = (COLS - width) // 2
    for r, c in cells:
        state.grid[top + r][left + c] = 1


def notes_for(state):
    """Ask music.py for this generation's notes. Until music.py is finished
    it returns None, so we play nothing instead of crashing."""
    births, deaths = state.changes()
    try:
        notes = music.map_generation_to_notes(births, deaths, state.count_living(), ROWS, COLS, SCALE)
    except Exception:
        return None
    return notes if notes else None


# ---- widgets ------------------------------------------------------------
class Button:
    def __init__(self, label, rect, action):
        self.label = label
        self.rect = pygame.Rect(rect)
        self.action = action

    def draw(self, screen, font, active=False, hover=False):
        fill = INK if active else (WHITE if not hover else (250, 247, 241))
        pygame.draw.rect(screen, fill, self.rect, border_radius=6)
        pygame.draw.rect(screen, INK, self.rect, 1, border_radius=6)
        text = font.render(self.label, True, PAPER if active else INK)
        screen.blit(text, text.get_rect(center=self.rect.center))


class Slider:
    def __init__(self, label, rect, low, high, value):
        self.label = label
        self.rect = pygame.Rect(rect)
        self.low, self.high, self.value = low, high, value
        self.dragging = False

    def knob_x(self):
        span = self.high - self.low
        return self.rect.x + (self.value - self.low) * self.rect.w // span

    def set_from_x(self, x):
        span = self.high - self.low
        ratio = min(max((x - self.rect.x) / self.rect.w, 0), 1)
        self.value = self.low + round(ratio * span)

    def draw(self, screen, font):
        screen.blit(font.render(self.label, True, INK), (self.rect.x - 92, self.rect.y - 9))
        pygame.draw.line(screen, INK, (self.rect.x, self.rect.centery), (self.rect.right, self.rect.centery), 3)
        knob = pygame.Rect(0, 0, 14, 22)
        knob.center = (self.knob_x(), self.rect.centery)
        pygame.draw.rect(screen, ACCENT, knob, border_radius=3)
        value = font.render(str(self.value), True, MUTED)
        screen.blit(value, (self.rect.right + 18, self.rect.y - 9))


# ---- the app ------------------------------------------------------------
class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Game of Life with Music")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 16)
        self.small = pygame.font.SysFont("arial", 14)
        self.bold = pygame.font.SysFont("arial", 17, bold=True)
        self.title = pygame.font.SysFont("arial", 22, bold=True)

        self.state = State(ROWS, COLS)
        self.engine = sound.SoundEngine()
        self.instrument = 0
        self.last_births, self.last_deaths = [], []
        self.last_notes = "-"
        self.timer = 0.0
        self.running = True

        place_centered(self.state, patterns.GLIDER)
        self.build_controls()

    def build_controls(self):
        x = PANEL_X + 16
        w2 = (PANEL_W - 16 * 2 - 10) // 2
        w3 = (PANEL_W - 16 * 2 - 20) // 3
        y = GRID_Y + 56
        self.buttons = [
            Button("Play / Pause", (x, y, w2, 36), self.state.toggle_play),
            Button("Step", (x + w2 + 10, y, w2, 36), self.step),
            Button("Clear", (x, y + 46, w2, 36), self.clear),
            Button("Random", (x + w2 + 10, y + 46, w2, 36), self.state.randomize),
        ]
        y = GRID_Y + 188
        for i, name in enumerate(PATTERNS):
            self.buttons.append(Button(name, (x + i * (w3 + 10), y, w3, 36),
                                       lambda n=name: place_centered(self.state, PATTERNS[n])))
        self.instrument_button = Button("", (x, GRID_Y + 284, PANEL_W - 32, 36), self.next_instrument)
        self.buttons.append(self.instrument_button)
        self.mute_button = Button("Mute", (x, GRID_Y + 452, w2, 36), self.engine.toggle_mute)
        self.buttons.append(self.mute_button)
        self.volume = Slider("Volume", (x + 92, GRID_Y + 384, 150, 12), 0, 10, self.engine.volume)
        self.speed = Slider("Speed", (x + 92, GRID_Y + 420, 150, 12), 1, 10, self.state.speed)
        self.sliders = [self.volume, self.speed]

    # actions
    def step(self):
        self.state.step_once()
        self.last_births, self.last_deaths = self.state.changes()
        notes = notes_for(self.state)
        if notes:
            self.engine.play(notes, INSTRUMENTS[self.instrument])
            self.last_notes = " ".join(music.note_name(n.midi) for n in notes)
        else:
            self.last_notes = "-"

    def clear(self):
        self.state.clear()
        self.engine.stop_all()
        self.last_births, self.last_deaths = [], []
        self.last_notes = "-"

    def next_instrument(self):
        self.instrument = (self.instrument + 1) % len(INSTRUMENTS)

    # input
    def handle(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cell = cell_at(event.pos)
            if cell is not None:
                self.state.toggle_cell(*cell)
                return
            for slider in self.sliders:
                if slider.rect.inflate(20, 24).collidepoint(event.pos):
                    slider.dragging = True
                    self.move_slider(slider, event.pos[0])
                    return
            for button in self.buttons:
                if button.rect.collidepoint(event.pos):
                    button.action()
                    return
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for slider in self.sliders:
                slider.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            for slider in self.sliders:
                if slider.dragging:
                    self.move_slider(slider, event.pos[0])
        elif event.type == pygame.KEYDOWN:
            keys = {
                pygame.K_SPACE: self.state.toggle_play, pygame.K_s: self.step,
                pygame.K_c: self.clear, pygame.K_r: self.state.randomize,
                pygame.K_m: self.engine.toggle_mute,
                pygame.K_1: lambda: place_centered(self.state, patterns.BLOCK),
                pygame.K_2: lambda: place_centered(self.state, patterns.BLINKER),
                pygame.K_3: lambda: place_centered(self.state, patterns.GLIDER),
                pygame.K_UP: lambda: self.state.set_speed(self.state.speed + 1),
                pygame.K_DOWN: lambda: self.state.set_speed(self.state.speed - 1),
            }
            if event.key in keys:
                keys[event.key]()
            self.speed.value = self.state.speed

    def move_slider(self, slider, x):
        slider.set_from_x(x)
        if slider is self.volume:
            self.engine.set_volume(slider.value)
        else:
            self.state.set_speed(slider.value)

    def update(self, seconds):
        if not self.state.playing:
            self.timer = 0.0
            return
        self.timer += seconds
        if self.timer >= 1 / steps_per_second(self.state.speed):
            self.timer = 0.0
            self.step()

    # drawing
    def draw(self):
        s = self.screen
        s.fill(PAPER)
        pygame.draw.rect(s, INK, (0, 0, WIDTH, TITLE_H))
        title = self.title.render("Game of Life with Music", True, PAPER)
        s.blit(title, title.get_rect(midleft=(MARGIN, TITLE_H // 2)))
        sub = self.small.render("BTIS2 Group 2 · click cells to make them alive or dead", True, LINE)
        s.blit(sub, sub.get_rect(midright=(WIDTH - MARGIN, TITLE_H // 2)))
        self.draw_grid()
        self.draw_panel()
        self.draw_status()
        pygame.display.flip()

    def draw_grid(self):
        s = self.screen
        pygame.draw.rect(s, WHITE, (GRID_X, GRID_Y, GRID_W, GRID_H))
        born = set(self.last_births)
        for r in range(ROWS):
            for c in range(COLS):
                if self.state.grid[r][c] == 1:
                    colour = BIRTH if (r, c) in born else INK
                    pygame.draw.rect(s, colour, (GRID_X + c * CELL + 1, GRID_Y + r * CELL + 1, CELL - 1, CELL - 1))
        for c in range(COLS + 1):
            x = GRID_X + c * CELL
            pygame.draw.line(s, LINE, (x, GRID_Y), (x, GRID_Y + GRID_H))
        for r in range(ROWS + 1):
            y = GRID_Y + r * CELL
            pygame.draw.line(s, LINE, (GRID_X, y), (GRID_X + GRID_W, y))
        pygame.draw.rect(s, INK, (GRID_X, GRID_Y, GRID_W + 1, GRID_H + 1), 2)

    def draw_panel(self):
        s = self.screen
        panel = pygame.Rect(PANEL_X, GRID_Y, PANEL_W, GRID_H + 1)
        pygame.draw.rect(s, PANEL, panel, border_radius=8)
        pygame.draw.rect(s, LINE, panel, 1, border_radius=8)
        x = PANEL_X + 16
        w2 = (PANEL_W - 16 * 2 - 10) // 2
        for label, y in [("SIMULATION", 24), ("PATTERNS", 158), ("INSTRUMENT", 254), ("SOUND & SPEED", 346)]:
            s.blit(self.bold.render(label, True, ACCENT), (x, GRID_Y + y))
        self.instrument_button.label = INSTRUMENTS[self.instrument] + "  ▸  next"
        self.mute_button.label = "Unmute" if self.engine.muted else "Mute"
        mouse = pygame.mouse.get_pos()
        for button in self.buttons:
            active = (button.label == "Play / Pause" and self.state.playing) or \
                     (button is self.mute_button and self.engine.muted)
            button.draw(s, self.font, active, button.rect.collidepoint(mouse))
        for slider in self.sliders:
            slider.draw(s, self.font)
        s.blit(self.small.render(self.engine.status(), True, MUTED), (x + w2 + 22, GRID_Y + 462))
        hint = "Space play · S step · C clear · R random"
        s.blit(self.small.render(hint, True, MUTED), (x, GRID_Y + GRID_H - 28))

    def draw_status(self):
        s = self.screen
        y = GRID_Y + GRID_H + MARGIN
        bar = pygame.Rect(MARGIN, y, WIDTH - 2 * MARGIN, STATUS_H)
        pygame.draw.rect(s, PANEL, bar, border_radius=8)
        pygame.draw.rect(s, LINE, bar, 1, border_radius=8)
        state = "Playing" if self.state.playing else ("Stopped: " + self.state.stop_reason if self.state.stopped else "Paused")
        parts = [
            "Generation: %d" % self.state.generation,
            "Living cells: %d" % self.state.count_living(),
            "Births: %d" % len(self.last_births),
            "Deaths: %d" % len(self.last_deaths),
            "Last notes: " + self.last_notes,
            state,
        ]
        text = self.font.render("   |   ".join(parts), True, INK)
        s.blit(text, text.get_rect(midleft=(MARGIN + 16, y + STATUS_H // 2)))

    def run(self):
        while self.running:
            seconds = self.clock.tick(60) / 1000
            for event in pygame.event.get():
                self.handle(event)
            self.update(seconds)
            self.draw()
        pygame.quit()


def main():
    App().run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
