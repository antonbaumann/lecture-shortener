#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os.path

from moviepy.editor import *
from scipy.io import wavfile

from util import arguments, audio, util, video

TEMP_DIR = '.tmp'
AUDIO_FILE_NAME = 'audio.wav'
DEVNULL = open(os.devnull, 'w')


def main():
    args = arguments.arguments()

    complete_clip = VideoFileClip(args.input_filename)
    audio.extract_audio_from_video(args.input_filename)
    sample_rate, audio_data = wavfile.read(os.path.join(TEMP_DIR, AUDIO_FILE_NAME))
    os.remove(os.path.join(TEMP_DIR, AUDIO_FILE_NAME))

    step_duration = args.step_duration if args.step_duration else args.min_silence_len / 10
    ranges = audio.detect_silence_ranges(
        audio_data=audio_data,
        sample_rate=sample_rate,
        min_silence_len=args.min_silence_len,
        step_duration=step_duration,
        silence_threshold=args.silence_threshold
    )

    util.show_saved_time_info(ranges)

    prompt = 'prompt'
    while prompt not in {'Y', 'y', ''}:
        prompt = input(f'[!] do you want to continue? [Y/n]: ')
        if prompt in {'n', 'N'}:
            exit(0)

    clips = video.generate_clips(ranges, complete_clip, args.speed_sound, args.speed_silence)

    print()
    concat_clip = concatenate_videoclips(clips, method='compose')
    concat_clip.write_videofile(args.output_filename, threads=4)


if __name__ == '__main__':
    main()
