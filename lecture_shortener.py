#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
import subprocess
import time

import moviepy.video.fx.all
import numpy as np
from moviepy.editor import *
from scipy.io import wavfile

import arguments

TEMP_DIR = '.tmp'
AUDIO_FILE_NAME = 'audio.wav'
DEVNULL = open(os.devnull, 'w')


def extract_audio_from_video(video_file):
    print('[i] extracting audio from video ...')
    if not os.path.exists(TEMP_DIR):
        os.mkdir(TEMP_DIR)
    command = f'ffmpeg -i {video_file} -ab 160k -ac 2 -ar 44100 ' \
        f'-vn {os.path.join(TEMP_DIR, AUDIO_FILE_NAME)} -y'
    subprocess.call(command, shell=True, stdout=DEVNULL)
    print('[✓] done!\n')


def get_energy(samples):
    return np.sum(np.power(samples, 2)) / float(len(samples))


def windows(samples, window_size, step_size):
    for start in range(0, len(samples), step_size):
        end = start + window_size
        if end >= len(samples):
            break
        yield samples[start:end]


def time_remaining(iteration, total_iterations, start):
    iterations_per_sec = (iteration + 1) / (time.time() - start)
    return (total_iterations - (iteration + 1)) / iterations_per_sec


def detect_silence_ranges(audio, sample_rate, min_silence_len, step_duration, silence_threshold):
    print('[i] detecting silence ranges ...')
    function_start = time.time()

    print('    - converting audio to mono')
    mono_audio = np.sum(audio, axis=1) / 2

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
    #todo: find out exact size of step count
    step_count = len(audio) // step_size

    start_loop = time.time()
    has_silent_audio = np.zeros((step_count))

    print(f'[i] finding silent ranges')
    for i, energy in enumerate(window_energy):
        if i % 1000 == 0:
            remaining = time_remaining(i, step_count, start_loop)
            print(f'\r    {i // 1000}k of {step_count // 1000}k  ETA: {round(remaining, 2)}s    ', end='')
        if energy <= silence_threshold:
            has_silent_audio[i] = 1

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

    duration = round(time.time() - function_start, 1)
    print(f'\n[i] took {duration} seconds')
    return ranges  # in seconds


def apply_speed_to_range(clip, range_to_modify, speed):
    subclip = clip.subclip(range_to_modify[0], range_to_modify[1])
    return moviepy.video.fx.all.speedx(subclip, factor=speed)


def format_seconds(seconds):
    ret = ''
    minutes = int(seconds / 60)
    hours = minutes // 60
    if hours != 0:
        ret += f'{hours}h'
    if hours != 0 or minutes % 60 != 0:
        ret += f' {minutes}m '
    ret += f'{int(seconds % 60)}s'
    return ret


def main():
    args = arguments.arguments()

    extract_audio_from_video(args.input_filename)
    complete_clip = VideoFileClip(args.input_filename)
    sample_rate, audio_data = wavfile.read(os.path.join(TEMP_DIR, AUDIO_FILE_NAME))
    os.remove(os.path.join(TEMP_DIR, AUDIO_FILE_NAME))

    step_duration = args.step_duration if args.step_duration else args.min_silence_len / 10
    ranges = detect_silence_ranges(
        audio=audio_data,
        sample_rate=sample_rate,
        min_silence_len=args.min_silence_len,
        step_duration=step_duration,
        silence_threshold=args.silence_threshold
    )

    saved_time = 0
    print('[i] silence ranges:')
    for range in ranges:
        saved_time += range[1] - range[0]
        print(f'    {range}')

    print()
    print(f'[i] saved time: {format_seconds(saved_time)}')
    prompt = 'prompt'
    while prompt not in {'Y', 'y', ''}:
        prompt = input(f'[!] do you want to continue? [Y/n]: ')
        if prompt in {'n', 'N'}:
            exit(0)

    video_len = complete_clip.duration

    clips = []
    print(f'[i] applying speed to clips')
    if ranges and len(ranges) != 0:
        if not ranges[0][0] == 0:
            clips.append(
                apply_speed_to_range(
                    complete_clip,
                    (0, ranges[0][0] - 1),
                    args.speed_sound
                )
            )

        start_apply_speed = time.time()
        for i, silence_range in enumerate(ranges):
            remaining = time_remaining(i, len(ranges), start_apply_speed)
            print(f'\r    {i + 1} of {len(ranges)}  ETA: {round(remaining, 2)} s    ', end='')
            clips.append(
                # todo fade in
                apply_speed_to_range(
                    complete_clip,
                    silence_range,
                    args.speed_silence
                )
                # todo fade out
            )
            if i < len(ranges) - 1:
                clips.append(
                    apply_speed_to_range(
                        complete_clip,
                        (silence_range[1] + 1, ranges[i + 1][0] - 1),
                        args.speed_sound
                    )
                )

        if ranges[-1][1] < video_len:
            clips.append(
                apply_speed_to_range(
                    complete_clip,
                    (ranges[-1][1] + 1, video_len),
                    args.speed_sound
                )
            )
    else:
        print("[i] no silence detected")
        clips.append(
            apply_speed_to_range(
                complete_clip,
                (0, video_len),
                args.speed_sound
            )
        )

    print()
    concat_clip = concatenate_videoclips(clips, method='compose')
    concat_clip.write_videofile(args.output_filename, threads=4)


if __name__ == '__main__':
    main()
