#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time

import moviepy.video.fx.all
import numpy as np
from scipy.io.wavfile import write

from util import util
from util import audio


def apply_speed_to_range(clip, range_to_modify, speed):
    subclip = clip.subclip(range_to_modify[0], range_to_modify[1])

    # extract unmodified audio data
    audio_data = subclip.audio
    audio_array = np.array(audio_data.to_soundarray())

    fast_audio_array = audio.apply_speed_to_audio(audio_array.T, speed)     # without modifying pitch!

    # fast_audio = moviepy.audio.io.AudioFileClip.AudioFileClip(fast_audio_array)

    # workaround in order to be able to create an audio file clip from the modified audio
    temp_file_name = ".tmp/" + str(int(range_to_modify[0])) + ".wav"
    write(temp_file_name, audio_data.fps, fast_audio_array.T)
    fast_audio = moviepy.audio.io.AudioFileClip.AudioFileClip(temp_file_name)

    fast_subclip = moviepy.video.fx.all.speedx(subclip, factor=speed)
    # guarantee that both the audio and video have the same duration
    fast_subclip = fast_subclip.set_duration(fast_audio.duration)
    fast_subclip = fast_subclip.set_audio(fast_audio)

    return fast_subclip


def generate_clips(ranges, complete_clip, speed_sound, speed_silence):
    print(f'[i] applying speed to clips')
    video_len = complete_clip.duration
    clips = []
    if ranges and len(ranges) != 0:
        if not ranges[0][0] == 0:
            clips.append(
                apply_speed_to_range(
                    complete_clip,
                    (0, ranges[0][0] - 1),
                    speed_sound
                )
            )

        start_apply_speed = time.time()
        for i, silence_range in enumerate(ranges):
            # remaining = util.time_remaining(i, len(ranges), start_apply_speed)
            # print(f'\r    {i + 1} of {len(ranges)}  ETA: {round(remaining, 2)} s    ', end='')
            print(f'\r    {i + 1} of {len(ranges)}', end='')
            clips.append(
                # todo fade in
                apply_speed_to_range(
                    complete_clip,
                    silence_range,
                    speed_silence
                )
                # todo fade out
            )
            if i < len(ranges) - 1:
                clips.append(
                    apply_speed_to_range(
                        complete_clip,
                        (silence_range[1] + 1, ranges[i + 1][0] - 1),
                        speed_sound
                    )
                )

        if ranges[-1][1] < video_len:
            clips.append(
                apply_speed_to_range(
                    complete_clip,
                    (ranges[-1][1] + 1, video_len),
                    speed_sound
                )
            )
    else:
        print("[i] no silence detected")
        clips.append(
            apply_speed_to_range(
                complete_clip,
                (0, video_len),
                speed_sound
            )
        )
    return clips
