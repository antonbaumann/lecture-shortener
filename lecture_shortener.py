import os.path
import subprocess
import time

import moviepy.video.fx.all
import numpy as np
from moviepy.editor import *
from scipy.io import wavfile

import util

TEMP_DIR = '.tmp'
AUDIO_FILE_NAME = 'audio.wav'


def extract_audio_from_video(video_file):
    print('[i] extracting audio from video ...')
    if not os.path.exists(TEMP_DIR):
        os.mkdir(TEMP_DIR)
    command = f'ffmpeg -i {video_file} -ab 160k -ac 2 -ar 44100 -vn {os.path.join(TEMP_DIR, AUDIO_FILE_NAME)}'
    subprocess.call(command, shell=True)


def get_energy(samples):
    return np.sum(np.power(samples, 2)) / float(len(samples))


def windows(samples, window_size, step_size):
    for start in range(0, len(samples), step_size):
        end = start + window_size
        if end >= len(samples):
            break
        yield samples[start:end]


def detect_silence_ranges(audio, sample_rate, min_silence_len, step_duration, silence_threshold):
    print('[i] detecting silence ranges ...')
    start = time.time()

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
            iterations_per_sec = (i + 1) / (time.time() - start_loop)
            time_remaining = (step_count - (i + 1)) / iterations_per_sec
            print(f'\r    {i // 1000}k of {step_count // 1000}k  ETA: {round(time_remaining, 2)}s    ', end='')
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
                start, stop = last_silent * step_size, (i - 1) * step_size  # converting from window pos -> frame pos
                if stop - start >= window_size:
                    ranges.append((start / sample_rate, stop / sample_rate))  # convert to seconds
                last_silent = -1

    duration = round(time.time() - start, 1)
    print(f'took {duration} seconds')
    return ranges  # in seconds


def apply_speed_to_range(clip, silence_range, speed):
    subclip = clip.subclip(silence_range[0], silence_range[1])
    return moviepy.video.fx.all.speedx(subclip, factor=speed)


def main():
    args = util.arguments()

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

    for range in ranges:
        print(range)

    video_len = complete_clip.duration

    clips = []
    if ranges and len(ranges) != 0:
        if not ranges[0][0] == 0:
            clips.append(
                apply_speed_to_range(
                    complete_clip,
                    (0, ranges[0][0] - 1),
                    args.speed_sound
                )
            )

        for i, silence_range in enumerate(ranges):
            print(f'\r{i + 1} of {len(ranges)}', end='')
            clips.append(
                apply_speed_to_range(
                    complete_clip,
                    silence_range,
                    args.speed_silence
                )
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
        clips.append(complete_clip)

    print()
    concat_clip = concatenate_videoclips(clips, method='compose')
    concat_clip.write_videofile(args.output_filename, threads=4)


if __name__ == '__main__':
    main()
