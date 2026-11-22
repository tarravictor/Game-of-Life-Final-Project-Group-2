# Game of Life with Music: Final Project, Group 2

Conway's Game of Life where every birth plays a note. Cells are born and die by the B3/S23 rule, and the births are turned into notes that are played on a generated instrument (Piano, Organ or Bell). All sounds are built from math (NumPy), so there are no recorded songs.

## What the prototype does

The current prototype (`main.py`) is text-only. It places a pattern (block, blinker or glider) on a small board, prints each generation as `#` (alive) and `.` (dead), and stops when the board is empty, stable, or the generation limit is reached. `music.py` turns births into notes and `sound.py` plays them on the chosen instrument. If there is no audio device, the app keeps running and the sound status is "Sound: unavailable".

## Requirements

- Python 3.10 or newer
- pygame (window, input, audio playback)
- numpy (building the tones)
- unittest (built in to Python, used for tests)

## Install

```
pip install -r requirements.txt
```

## Run

```
python main.py
```

Optional: choose the pattern, board size and number of generations.

```
python main.py glider 8 8 12
```

The arguments are: pattern (`block`, `blinker` or `glider`), rows, columns, maximum generations.

## Run the tests

```
python -m unittest
```

## Who wrote which file

| File | Owner | Job |
|---|---|---|
| `music.py` | Manalili | Rules that turn births and deaths into notes (`Note`, `midi_to_freq`) |
| `sound.py` | Diego | Builds the instrument tones and plays the notes (`SoundEngine`) |
| `test_sound.py` | Diego | Tests for `sound.py` |
| `main.py` | Tarra | Text prototype: reads input and prints generations |
| `requirements.txt` | Diego | Libraries to install (pygame, numpy) |

## Members

- Victor Danielle Tarra
- Joaquin Carmelo Armas
- Ethan Austin Manalili
- Ethan Jarren Diego
- Rain Andrei Tumulac