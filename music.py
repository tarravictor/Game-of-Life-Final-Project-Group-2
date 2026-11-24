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

# My own settings for the rules
BASE_MIDI = 60           # lowest melody note (middle C)
OCTAVES = 2              # the rows of the board are spread over 2 octaves
BASS_DROP = 24           # the bass note sits 2 octaves below the melody
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_name(midi):
    """60 -> 'C4'. Used in the status bar."""
    # The 12 names repeat every octave, and middle C (60) starts octave 4
    name = NOTE_NAMES[midi % 12]
    octave = midi // 12 - 1
    return name + str(octave)


def midi_to_freq(midi):
    """A4 (69) = 440 Hz. Diego's sound.py calls this."""
    # f = 440 x 2^((m - 69) / 12): every 12 steps up doubles the frequency
    return 440 * 2 ** ((midi - 69) / 12)


def _scale_steps(scale):
    # scale can be a name from SCALES (like "Pentatonic") or a list of steps
    if isinstance(scale, str):
        if scale not in SCALES:
            raise ValueError("Unknown scale: " + scale)
        return SCALES[scale]
    if len(scale) == 0:
        raise ValueError("A scale needs at least one step.")
    return list(scale)


def _ladder(scale):
    # Every melody note we can use, from lowest to highest
    steps = _scale_steps(scale)
    notes = []
    for octave in range(OCTAVES):
        for step in steps:
            notes.append(BASE_MIDI + 12 * octave + step)
    return sorted(notes)


def _check_cell(row, col, rows, cols):
    if row < 0 or row >= rows or col < 0 or col >= cols:
        raise ValueError("Cell (%s, %s) is outside the %sx%s board." % (row, col, rows, cols))


def _pan(col, cols):
    # Left edge of the board = 0, right edge = 1
    if cols == 1:
        return 0.5
    return col / (cols - 1)


def row_to_midi(row, rows, scale):
    """RULE: row of a birth -> pitch. Row 0 (top) = highest note.
    Raise ValueError if row is outside 0..rows-1."""
    if row < 0 or row > rows - 1:
        raise ValueError("Row %s is outside 0..%s." % (row, rows - 1))

    ladder = _ladder(scale)
    top = len(ladder) - 1
    if rows == 1:
        return ladder[top]      # only one row, so it is also the top row

    # Row 0 lands on the highest note, the last row on the lowest note,
    # and the rows in between are spread out evenly
    position = (rows - 1 - row) / (rows - 1)
    return ladder[round(position * top)]


def population_volume(living, total_cells):
    """RULE: more living cells -> louder. Return 0.3 .. 1.0."""
    if total_cells <= 0:
        raise ValueError("total_cells must be more than 0.")

    share = living / total_cells        # 0 = empty board, 1 = every cell alive
    share = max(0, min(1, share))       # keep it between 0 and 1
    return round(0.3 + 0.7 * share, 4)   # rounded so 50% gives a clean 0.65


def map_generation_to_notes(births, deaths, living, rows, cols, scale):
    """Apply all rules to one generation.
    births/deaths: lists of (row, col). Return list of Note
    (at most MAX_NOTES melody notes, plus an optional bass note)."""
    births = list(births)
    deaths = list(deaths)

    # Check every cell first so a bad one never gives half a result
    for row, col in births + deaths:
        _check_cell(row, col, rows, cols)

    volume = population_volume(living, rows * cols)
    notes = []

    # Melody: each birth plays one note. If more than MAX_NOTES cells are
    # born, only the first MAX_NOTES are played.
    for row, col in births[:MAX_NOTES]:
        pitch = row_to_midi(row, rows, scale)
        notes.append(Note(pitch, volume, _pan(col, cols), "melody"))

    # Bass: if anything died, add ONE bass note. Its pitch comes from the
    # average row of the deaths (same row rule as the melody), 2 octaves lower.
    if len(deaths) > 0:
        total_rows = 0
        for row, col in deaths:
            total_rows = total_rows + row
        average_row = round(total_rows / len(deaths))
        bass_pitch = row_to_midi(average_row, rows, scale) - BASS_DROP
        notes.append(Note(bass_pitch, volume, 0.5, "bass"))

    return notes


def all_midis(rows, scale):
    """Every MIDI note your rules can produce (so sounds can be pre-loaded)."""
    found = set()
    for row in range(rows):
        melody = row_to_midi(row, rows, scale)
        found.add(melody)
        found.add(melody - BASS_DROP)
    return sorted(found)


def describe_notes(notes):
    """Short text for the status bar, e.g. 'C4, E4, G5 + bass C2'."""
    melody_names = []
    bass_names = []
    for note in notes:
        if note.kind == "bass":
            bass_names.append(note_name(note.midi))
        else:
            melody_names.append(note_name(note.midi))

    parts = []
    if len(melody_names) > 0:
        parts.append(", ".join(melody_names))
    if len(bass_names) > 0:
        parts.append("bass " + ", ".join(bass_names))

    if len(parts) == 0:
        return "no notes"
    return " + ".join(parts)
