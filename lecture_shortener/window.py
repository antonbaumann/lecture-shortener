import math
import time

import numpy as np

from lecture_shortener import util, audio


class WindowGenerator:
    def __init__(self, audio_data, window_size, step_size):
        self.audio_data = audio_data
        self.window_size = window_size
        self.step_size = step_size

        self.position = 0

        self.start = time.time()
        self.chunk_size = math.gcd(window_size, step_size)
        self.cache_size = window_size // self.chunk_size
        self.cache = Cache(self.cache_size)
        self.init_cache()

    def init_cache(self):
        for i in range(self.chunk_size - 1):
            self.cache.add(audio.get_energy(self.audio_data[i * self.chunk_size:(i + 1) * self.chunk_size]))

    def has_next(self):
        return self.position * self.chunk_size < len(self.audio_data)

    def progress(self):
        remaining = util.time_remaining(self.position, len(self.audio_data) // self.chunk_size, self.start)
        print(f'\r{self.position} of {len(self.audio_data) // self.chunk_size}  ETA: {remaining}', end='')

    def next_window(self):
        self.cache.add(
            audio.get_energy(
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
        return audio.get_energy(self.data)
