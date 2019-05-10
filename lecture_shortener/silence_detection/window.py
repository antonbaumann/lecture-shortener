import math
import time

import numpy as np

from silence_detection import util, silence


class WindowGenerator:
    def __init__(self, audio_data, window_size, step_size):
        self.audio_data = audio_data
        self.window_size = window_size
        self.step_size = step_size

        self.position = 0
        self.nr_windows = int((len(self.audio_data) - self.window_size + self.step_size) // self.step_size)

        self.start_time = time.time()
        self.chunk_size = math.gcd(window_size, step_size)
        self.cache = Cache(window_size // self.chunk_size)
        self._init_cache()

    def _init_cache(self):
        for i in range(self.cache.size - 1):
            self.cache.add(silence.get_energy(self.audio_data[i * self.chunk_size:(i + 1) * self.chunk_size]))

    def has_next(self):
        return self.position < self.nr_windows

    def progress(self):
        remaining = util.time_remaining(self.position, len(self.audio_data) // self.chunk_size, self.start_time)
        print(f'\r{self.position} of {len(self.audio_data) // self.chunk_size}  ETA: {remaining}', end='')

    def next_window(self):
        self.cache.add(
            silence.get_energy(
                self.audio_data[self.cache.index * self.chunk_size: (self.cache.index + 1) * self.chunk_size]
            )
        )
        self.position += 1
        return self.cache.get_energy()


class Cache:
    def __init__(self, size):
        self.size = size
        self.data = np.zeros(self.size)
        self.index = 0

    def add(self, value):
        self.data[self.index % self.size] = value
        self.index += 1

    def get_energy(self):
        return sum(self.data) / self.size
