import unittest

from silence_detection import window, silence


class TestWindowGenerator(unittest.TestCase):

    def test_init_cache(self):
        audio_data = [23, 24, 25, 26, 24, 23, 22, 20, 18]
        generator = window.WindowGenerator(audio_data, window_size=6, step_size=2)
        expected = [silence.get_energy([23, 24]), silence.get_energy([25, 26]), 0]
        self.assertListEqual(generator.cache.data.tolist(), expected)

    def test_next_window(self):
        audio_data = [23, 24, 25, 26, 24, 23, 22, 20, 18, 2, 5, 1, 0, 4, 53, 0]
        step_size = 2
        window_size = 6
        expected = [silence.get_energy(audio_data[i:i+window_size]) for i in range(0, len(audio_data) - window_size +1, step_size)]
        generator = window.WindowGenerator(audio_data, window_size=6, step_size=2)
        result = []
        while generator.has_next():
            result.append(generator.next_window())
        self.assertListEqual(expected, result)
