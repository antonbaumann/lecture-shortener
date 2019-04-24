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

    print('  - converting audio to mono')
    mono_audio = np.sum(audio, axis=1) / 2

    print('  - finding maximum amplitude')
    max_amplitude = np.max(mono_audio)
    max_energy = get_energy([max_amplitude])

    window_size = int(min_silence_len * sample_rate / 1000)
    step_size = int(step_duration * sample_rate / 1000)

    sample_windows = windows(
        samples=mono_audio,
        window_size=window_size,
        step_size=step_size
    )

    window_energy = (get_energy(w) / max_energy for w in sample_windows)

    ranges_silent = []
    ranges_sound = []

    last_frame_silent = False
    last_transition = -1
    length = 0
    for i, energy in enumerate(window_energy):
        length += 1
        current_frame_silent = energy <= silence_threshold
        if current_frame_silent != last_frame_silent:  # transition
            if last_transition == -1:
                last_transition = 0
                continue
            if last_frame_silent:
                last_frame_silent = False
                ranges_sound.append((last_transition, i - 1))
                last_transition = i
            else:
                last_frame_silent = True
                ranges_silent.append((last_transition, i - 1))
                last_transition = i

    if last_transition < length:
        if last_frame_silent:
            ranges_sound.append((last_transition, length - 1))
        else:
            ranges_silent.append((last_transition, length - 1))

    duration = round(time.time() - start, 1)
    print(f'took {duration} seconds')
    return ranges_silent, ranges_sound


def apply_speed_to_range(clip, silence_range, speed):
    subclip = clip.subclip(silence_range[0] / 1000, silence_range[1] / 1000)
    return moviepy.video.fx.all.speedx(subclip, factor=speed)


def main():
    args = util.arguments()

    extract_audio_from_video(args.input_filename)

    complete_clip = VideoFileClip(args.input_filename)
    sample_rate, audio_data = wavfile.read(os.path.join(TEMP_DIR, AUDIO_FILE_NAME))
    # frame_rate = complete_clip.fps

    os.remove(os.path.join(TEMP_DIR, AUDIO_FILE_NAME))

    step_duration = args.step_duration if args.step_duration else args.min_silence_len / 10
    silence_ranges, sound_ranges = detect_silence_ranges(
        audio=audio_data,
        sample_rate=sample_rate,
        min_silence_len=args.min_silence_len,
        step_duration=step_duration,
        silence_threshold=args.silence_threshold
    )

    for r in silence_ranges:
        print(r)

    video_len = complete_clip.duration * 1000

    clips = []
    if silence_ranges and len(silence_ranges) != 0:
        if not silence_ranges[0][0] == 0:
            clips.append(
                apply_speed_to_range(
                    complete_clip,
                    (0, silence_ranges[0][0] - 1),
                    args.speed_sound
                )
            )

        for i, silence_range in enumerate(silence_ranges):
            print(f'\r{i + 1} of {len(silence_ranges)}', end='')
            clips.append(
                apply_speed_to_range(
                    complete_clip,
                    silence_range,
                    args.speed_silence
                )
            )
            if i < len(silence_ranges) - 1:
                clips.append(
                    apply_speed_to_range(
                        complete_clip,
                        (silence_range[1] + 1, silence_ranges[i + 1][0] - 1),
                        args.speed_sound
                    )
                )

        if silence_ranges[-1][1] < video_len:
            clips.append(
                apply_speed_to_range(
                    complete_clip,
                    (silence_ranges[-1][1] + 1, video_len),
                    args.speed_sound
                )
            )
    else:
        print("[i] no silence detected")
        clips.append(complete_clip)

    print()
    concat_clip = concatenate_videoclips(clips, method='chain')
    concat_clip.write_videofile(args.output_filename)


if __name__ == '__main__':
    main()
