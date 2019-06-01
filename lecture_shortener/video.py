#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path
import time

import moviepy.video.fx.all
import numpy as np
from scipy.io import wavfile

from lecture_shortener import globals, audio, util


def _apply_speed_to_range(clip, range_to_modify, speed, is_silent):
    subclip = clip.subclip(range_to_modify[0], range_to_modify[1])

    # We only need to care about preserving the audio's pitch, if the range to modify is not silent
    if is_silent:
        fast_subclip = moviepy.video.fx.all.speedx(subclip, factor=speed)
    else:
        # extract unmodified audio data
        audio_data = subclip.audio
        sound_array = audio_data.to_soundarray()
        audio_array = np.array(sound_array)

        fast_audio_array = audio.apply_speed_to_audio(audio_array.T, speed)  # without modifying pitch!

        # workaround in order to be able to create an audio file clip from the modified audio
        # saves .wav chunks in TEMPDIR
        temp_file_path = os.path.join(globals.TEMP_DIR, f'{int(range_to_modify[0] * 100)}.wav')
        wavfile.write(temp_file_path, audio_data.fps, fast_audio_array.T)
        fast_audio = moviepy.audio.io.AudioFileClip.AudioFileClip(temp_file_path)

        # apply speed to subclip
        fast_subclip = moviepy.video.fx.all.speedx(subclip, factor=None, final_duration=fast_audio.duration)
        fast_subclip = fast_subclip.set_audio(fast_audio)

    return fast_subclip


# applies silence- and sound-speed to video
def generate_clips(ranges, complete_clip, speed_sound, speed_silence):
    # utility functions: return start or end of silence_detection range in seconds
    def start_time(r) -> int:
        return r[0]

    def end_time(r) -> int:
        return r[1]

    print(f'[i] applying speed to clips')
    video_len = complete_clip.duration
    clips = []

    # check if no silence range is detected
    if not ranges or len(ranges) == 0:
        print("[i] no silence_detection detected")
        clips.append(
            _apply_speed_to_range(
                complete_clip,
                (0, video_len),
                speed_sound,
                is_silent=False
            )
        )
        return clips

    # beginning of video is silent
    if not start_time(ranges[0]) == 0:
        clips.append(
            _apply_speed_to_range(
                complete_clip,
                (0, start_time(ranges[0])),
                speed_sound,
                is_silent=False
            )
        )

    start = time.time()
    for i in range(len(ranges)):
        remaining = util.time_remaining(i, len(ranges), start)
        print(f'\r    {i + 1} of {len(ranges)}  ETA: {round(remaining, 2)} s    ', end='')
        clips.append(
            _apply_speed_to_range(
                complete_clip,
                ranges[i],
                speed_silence,
                is_silent=True
            )
        )
        if i < len(ranges) - 1:
            clips.append(
                _apply_speed_to_range(
                    complete_clip,
                    (end_time(ranges[i]), start_time(ranges[i + 1])),
                    speed_sound,
                    is_silent=False
                )
            )

    if ranges[-1][1] < video_len:
        clips.append(
            _apply_speed_to_range(
                complete_clip,
                (end_time(ranges[-1]), video_len),
                speed_sound,
                is_silent=False
            )
        )

    return clips
