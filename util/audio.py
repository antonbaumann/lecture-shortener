#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import time

import numpy as np

import lecture_shortener as ls
from util import util


def extract_audio_from_video(video_file):
    print('[i] extracting audio from video ...')
    if not os.path.exists(ls.TEMP_DIR):
        os.mkdir(ls.TEMP_DIR)
    command = f'ffmpeg -i {video_file} -ab 160k -ac 2 -ar 44100 ' \
        f'-vn {os.path.join(ls.TEMP_DIR, ls.AUDIO_FILE_NAME)} -y'
    subprocess.call(command, shell=True, stdout=ls.DEVNULL)
    print('[✓] done!\n')


def get_energy(samples):
    return np.sum(np.power(samples, 2)) / float(len(samples))


def windows(samples, window_size, step_size):
    for start in range(0, len(samples), step_size):
        end = start + window_size
        if end >= len(samples):
            break
        yield samples[start:end]


def _detect_samples_with_silent_audio(window_energy, step_count, silence_threshold):
    start_loop = time.time()
    has_silent_audio = np.zeros((step_count))
    for i, energy in enumerate(window_energy):
        if i % 1000 == 0:
            remaining = util.time_remaining(i, step_count, start_loop)
            print(f'\r    {i // 1000}k of {step_count // 1000}k  ETA: {round(remaining, 2)}s    ', end='')
        if energy <= silence_threshold:
            has_silent_audio[i] = 1
    return has_silent_audio


def _generate_ranges_from_array(has_silent_audio, window_size, step_size, sample_rate):
    ranges = []
    last_silent = -1
    for i, silent in enumerate(has_silent_audio):
        if silent == 1:
            if last_silent < 0:  # transition from sound -> silent
                last_silent = i
        else:
            if last_silent >= 0:  # transition from silence -> sound
                padding_size = sample_rate * 1  # one second padding so dont cut sound off
                start = last_silent * step_size + padding_size
                stop = (i - 1) * step_size - padding_size
                if stop - start >= window_size:
                    ranges.append((start / sample_rate, stop / sample_rate))  # convert to seconds
                last_silent = -1
    return ranges


def detect_silence_ranges(audio_data, sample_rate, min_silence_len, step_duration, silence_threshold):
    print('[i] detecting silence ranges ...')
    function_start = time.time()

    print('    - converting audio to mono')
    mono_audio = np.sum(audio_data, axis=1) / 2

    print('    - finding maximum amplitude')
    max_amplitude = np.max(mono_audio)
    max_energy = get_energy([max_amplitude])

    window_size = int(min_silence_len * sample_rate / 1000)  # size of window in frame count
    step_size = int(step_duration * sample_rate / 1000)  # step size in frame count

    print(f'[i] window size: {window_size} frames')
    print(f'[i] step size: {step_size} frames')

    sample_windows = windows(
        samples=mono_audio,
        window_size=window_size,
        step_size=step_size
    )

    window_energy = (get_energy(w) / max_energy for w in sample_windows)
    # todo: find out exact size of step count
    step_count = len(audio_data) // step_size

    print(f'[i] finding silent ranges')
    has_silent_audio = _detect_samples_with_silent_audio(window_energy, step_count, silence_threshold)
    ranges = _generate_ranges_from_array(has_silent_audio, window_size, step_size, sample_rate)

    duration = round(time.time() - function_start, 1)
    print(f'\n[i] took {duration} seconds')
    return ranges  # in seconds
