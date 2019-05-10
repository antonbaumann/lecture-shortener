#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from moviepy.editor import *

from lecture_shortener import audio, arguments, util, video, globals
from silence_detection import silence


def main():
    args = arguments.arguments()

    # audio processing
    sample_rate, audio_data = audio.get_audio_data(args.input_filename, args.threads)
    step_duration = args.step_duration if args.step_duration else args.min_silence_len / 10
    ranges = silence.detect_silence_ranges(
        audio_data=audio_data,
        sample_rate=sample_rate,
        min_silence_len=args.min_silence_len,
        step_duration=step_duration,
        silence_threshold=args.silence_threshold,
        verbose=True,
        progress=True,
    )

    util.show_saved_time_info(ranges)

    prompt = 'prompt'
    while prompt not in {'Y', 'y', ''}:
        prompt = input(f'[!] do you want to continue? [Y/n]: ')
        if prompt in {'n', 'N'}:
            exit(0)

    # video processing
    complete_clip = VideoFileClip(args.input_filename)
    clips = video.generate_clips(
        ranges,
        complete_clip,
        args.speed_sound,
        args.speed_silence
    )
    print()
    concat_clip = concatenate_videoclips(clips, method='compose')
    concat_clip.write_videofile(args.output_filename, threads=args.threads)

    util.clear_dir(globals.TEMP_DIR)


if __name__ == '__main__':
    main()