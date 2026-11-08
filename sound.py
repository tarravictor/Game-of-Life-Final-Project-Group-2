"""sound.py - Generated instrument tones and playback.  Owner: Diego
NumPy builds the waves; pygame.mixer plays them. No recorded songs."""

import numpy as np
import pygame
from music import midi_to_freq   # from Manalili

SAMPLE_RATE = 44100


def make_time(seconds):
    return np.linspace(0, seconds, int(SAMPLE_RATE * seconds), endpoint=False)


def normalize(wave):
    return wave / np.max(np.abs(wave))


def piano(freq):
    """Return a NumPy array of samples (about 0.5-1.5 s long)."""
    t = make_time(1.0)
    wave = np.zeros(len(t))
    for k in range(1, 5):
        wave = wave + np.sin(2 * np.pi * freq * k * t) / k
    attack = np.minimum(t / 0.005, 1.0)
    wave = wave * attack * np.exp(-4 * t)
    return normalize(wave)


def organ(freq):
    t = make_time(0.8)
    wave = np.zeros(len(t))
    amps = [1.0, 0.5, 0.25]
    for i in range(len(amps)):
        wave = wave + amps[i] * np.sin(2 * np.pi * freq * (i + 1) * t)
    attack = np.minimum(t / 0.03, 1.0)
    release = np.minimum((0.8 - t) / 0.08, 1.0)
    return normalize(wave * attack * release)


def bell(freq):
    t = make_time(1.5)
    wave = np.zeros(len(t))
    ratios = [1.0, 2.76, 5.4, 8.93]
    amps = [1.0, 0.6, 0.4, 0.25]
    for i in range(len(ratios)):
        wave = wave + amps[i] * np.sin(2 * np.pi * freq * ratios[i] * t)
    attack = np.minimum(t / 0.002, 1.0)
    return normalize(wave * attack * np.exp(-3 * t))


INSTRUMENTS = {"Piano": piano, "Organ": organ, "Bell": bell}   # at least 3


class SoundEngine:
    def __init__(self, enabled=True):
        """If pygame.mixer is not available, set self.available = False
        and keep working silently."""
        self.available = True
        self.muted = not enabled
        self.volume = 7
        self.sounds = {}
        try:
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1)
            pygame.mixer.set_num_channels(32)
        except (pygame.error, NotImplementedError):
            self.available = False

    @property
    def status(self):
        """'on', 'muted' or 'unavailable' (shown in the status bar)."""
        if not self.available:
            return "unavailable"
        if self.muted:
            return "muted"
        return "on"

    def build(self, instrument, midi):
        key = (instrument, midi)
        if key not in self.sounds:
            wave = INSTRUMENTS[instrument](midi_to_freq(midi))
            data = (wave * 0.5 * 32767).astype(np.int16)
            self.sounds[key] = pygame.mixer.Sound(buffer=data.tobytes())
        return self.sounds[key]

    def preload(self, midis):
        """Build a pygame Sound for every instrument x midi in advance."""
        if not self.available:
            return
        for name in INSTRUMENTS:
            for midi in midis:
                self.build(name, midi)

    def set_volume(self, level):
        """Whole number 0..10. Clamp out-of-range values."""
        level = int(level)
        if level < 0:
            level = 0
        if level > 10:
            level = 10
        self.volume = level

    def toggle_mute(self):
        self.muted = not self.muted

    def play(self, notes, instrument):
        """Play a list of Note on the named instrument. Return how many started.
        Raise ValueError for an unknown instrument."""
        if instrument not in INSTRUMENTS:
            raise ValueError("Unknown instrument: " + str(instrument))
        if not self.available or self.muted:
            return 0
        started = 0
        for note in notes:
            sound = self.build(instrument, note.midi)
            sound.set_volume(self.volume / 10)
            if sound.play() is not None:
                started = started + 1
        return started

    def stop_all(self):
        """Stop every sound (used by Clear and Reset)."""
        if self.available:
            pygame.mixer.stop()
