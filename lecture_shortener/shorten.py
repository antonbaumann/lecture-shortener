#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from moviepy.editor import *

from lecture_shortener import audio, util, video, globals
from pysilence import silence


def shorten(
    input_path,
    output_path,
    speed_sound=1.6,
    speed_silence=5.0,
    min_silence_len=2000,
    step_duration=None,
    silence_threshold=0.1,
    nr_threads=2,
    verbose=False,
    progress=False,
):
    # audio processing
    sample_rate, audio_data = audio.get_audio_data(input_path, nr_threads)
    step_duration = step_duration if step_duration else min_silence_len / 10
    ranges = silence.detect_silence_ranges(
        audio_data=audio_data,
        sample_rate=sample_rate,
        min_silence_len=min_silence_len,
        step_duration=step_duration,
        silence_threshold=silence_threshold,
        verbose=verbose,
        progress=progress,
    )

    util.show_saved_time_info(ranges)

    prompt = 'prompt'
    while prompt not in {'Y', 'y', ''}:
        prompt = input(f'[!] do you want to continue? [Y/n]: ')
        if prompt in {'n', 'N'}:
            exit(0)

    # video processing
    complete_clip = VideoFileClip(input_path)
    clips = video.generate_clips(
        ranges,
        complete_clip,
        speed_sound,
        speed_silence
    )
    print()
    concat_clip = concatenate_videoclips(clips, method='compose')
    concat_clip.write_videofile(output_path, threads=nr_threads)

    util.clear_dir(globals.TEMP_DIR)
