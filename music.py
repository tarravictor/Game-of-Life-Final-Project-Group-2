"""music.py - Rules that turn simulation data into notes.  Owner: Manalili
Pure functions only: no sound playing here."""

from collections import namedtuple

Note = namedtuple("Note", "midi volume pan kind")
# midi: note number (60 = middle C) | volume: 0..1 | pan: 0 left .. 1 right
# kind: "melody" or "bass"

SCALES = {
    "Pentatonic": [0, 2, 4, 7, 9],
    "Major":      [0, 2, 4, 5, 7, 9, 11],
    # add more if you like
}
MAX_NOTES = 5            # spec: cap notes per beat


def note_name(midi):
    """60 -> 'C4'. Used in the status bar."""
    # TODO


def midi_to_freq(midi):
    """A4 (69) = 440 Hz. Diego's sound.py calls this."""
    # TODO


def row_to_midi(row, rows, scale):
    """RULE: row of a birth -> pitch. Row 0 (top) = highest note.
    Raise ValueError if row is outside 0..rows-1."""
    # TODO


def population_volume(living, total_cells):
    """RULE: more living cells -> louder. Return 0.3 .. 1.0."""
    # TODO


def map_generation_to_notes(births, deaths, living, rows, cols, scale):
    """Apply all rules to one generation.
    births/deaths: lists of (row, col). Return list of Note
    (at most MAX_NOTES melody notes, plus an optional bass note)."""
    # TODO


def all_midis(rows, scale):
    """Every MIDI note your rules can produce (so sounds can be pre-loaded)."""
    # TODO


def describe_notes(notes):
    """Short text for the status bar, e.g. 'C4, E4, G5 + bass C2'."""
    # TODO
