#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os

from lecture_shortener import shorten


# check if file exists
def validate_input_file(p, filepath) -> str:
    if not os.path.exists(filepath):
        p.error(f'The file {filepath} does not exist.')
    else:
        return filepath


# check if output file already exists
# if not check if dir does already exist
def validate_output_file(p, filepath) -> str:
    abspath = os.path.abspath(filepath)
    dirname = os.path.dirname(abspath)
    if os.path.isfile(abspath):
        p.error(f'The file {filepath} does already exist.')
    elif not os.path.exists(dirname):
        p.error(f'The directory {dirname} does not exist.')
    else:
        return filepath


def validate_float_positive(n) -> float:
    try:
        n = float(n)
        if n <= 0:
            raise argparse.ArgumentTypeError(f'{n} must be greater than 0')
        return n
    except ValueError:
        raise argparse.ArgumentTypeError(f'{n} could not be converted to float')


def validate_int_positive(n) -> int:
    try:
        n = int(n)
        if n <= 0:
            raise argparse.ArgumentTypeError(f'{n} must be greater than 0')
        return n
    except ValueError:
        raise argparse.ArgumentTypeError(f'{n} could not be converted to int')


def arguments():
    parser = argparse.ArgumentParser(description='Speed up lectures')
    parser.add_argument(
        '-i',
        dest='input_filename',
        required=True,
        help='input file path',
        metavar='INFILE',
        type=lambda x: validate_input_file(parser, x)
    )
    parser.add_argument(
        '-o',
        dest='output_filename',
        required=True,
        help='output file path',
        metavar='OUTFILE',
        type=lambda x: validate_output_file(parser, x)
    )
    parser.add_argument(
        '--speed-sound',
        metavar='SPEED_SOUND',
        type=lambda x: validate_float_positive(x),
        default=1.6,
        help='general video speed',
    )
    parser.add_argument(
        '--speed-silence',
        metavar='SPEED_SILENCE',
        type=lambda x: validate_float_positive(x),
        default=5.0,
        help='video speed during silence',
    )
    parser.add_argument(
        '--min-silence-len',
        type=lambda x: validate_int_positive(x),
        default=2000,
        help='section will be labeled as `silent` if silence is longer than `min-silence-len` in ms',
    )
    parser.add_argument(
        '--silence-threshold',
        type=float,
        default=0.1,
        help='frame is `silent` if volume is smaller than `silence-threshold',
    )
    parser.add_argument(
        '--step-duration',
        type=lambda x: validate_int_positive(x),
        default=None,
        help='check every n milliseconds for silence',
    )
    parser.add_argument(
        '--threads',
        metavar='THREADS',
        type=lambda x: validate_int_positive(x),
        default=2,
        help='general video speed',
    )
    return parser.parse_args()


args = arguments()
shorten.shorten(
    input_path=args.input_filename,
    output_path=args.output_filename,
    speed_sound=args.speed_sound,
    speed_silence=args.speed_silence,
    min_silence_len=args.min_silence_len,
    silence_threshold=args.silence_threshold,
    step_duration=args.step_duration,
    nr_threads=args.threads,
    verbose=True,
    progress=True,
)
