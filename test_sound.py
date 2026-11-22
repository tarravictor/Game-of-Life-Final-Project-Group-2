"""test_sound.py - Tests for sound.py (runs without an audio device)."""

from music import Note
import sound
import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


def fake_freq(midi):
    return 440 * 2 ** ((midi - 69) / 12)


class TestSoundEngine(unittest.TestCase):
    def setUp(self):
        patcher = patch("music.midi_to_freq", side_effect=fake_freq)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.engine = sound.SoundEngine()

    def test_play_returns_number_of_notes(self):
        notes = [Note(60, 1.0, 0.5, "melody"), Note(36, 0.8, 0.5, "bass")]
        self.assertEqual(self.engine.play(notes, "Piano"), 2)

    def test_unknown_instrument(self):
        with self.assertRaises(ValueError):
            self.engine.play([Note(60, 1.0, 0.5, "melody")], "Kazoo")

    def test_muted_plays_nothing(self):
        self.engine.toggle_mute()
        self.assertEqual(self.engine.status(), "Sound: muted")
        self.assertEqual(self.engine.play(
            [Note(60, 1.0, 0.5, "melody")], "Bell"), 0)

    def test_volume_is_clamped(self):
        self.engine.set_volume(99)
        self.assertEqual(self.engine.volume, 10)
        self.engine.set_volume(-3)
        self.assertEqual(self.engine.volume, 0)

    def test_no_audio_device(self):
        self.engine.available = False
        self.assertEqual(self.engine.status(), "Sound: unavailable")
        self.assertEqual(self.engine.play(
            [Note(60, 1.0, 0.5, "melody")], "Organ"), 0)


if __name__ == "__main__":
    unittest.main()
