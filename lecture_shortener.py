import argparse
import os.path
import subprocess

import moviepy.video.fx.all
from moviepy.editor import *
from pydub import AudioSegment, silence

TEMP_DIR = '.tmp'
AUDIO_FILE_NAME = 'audio.wav'


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
        default=1500,
        help='section will be labeled as `silent` if silence is longer than `silence_threshold` in seconds',
    )
    return parser.parse_args()


def extract_audio_from_video(video_file):
    print('[i] extracting audio from video ...')
    if not os.path.exists(TEMP_DIR):
        os.mkdir(TEMP_DIR)
    command = f'ffmpeg -i {video_file} -ab 160k -ac 2 -ar 44100 -vn {os.path.join(TEMP_DIR, AUDIO_FILE_NAME)}'
    subprocess.call(command, shell=True)


def detect_silence_ranges(audio, min_silence_len, silence_threshold=-16) -> list:
    print('[i] detecting silence ranges ...')
    return silence.detect_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=-silence_threshold
    )


def apply_speed_to_range(clip, silence_range, speed):
    subclip = clip.subclip(silence_range[0] / 1000, silence_range[1] / 1000)
    return moviepy.video.fx.all.speedx(subclip, factor=speed)


def main():
    args = arguments()

    extract_audio_from_video(args.input_filename)

    audio_segment = AudioSegment.from_wav(f'{TEMP_DIR}/{AUDIO_FILE_NAME}')
    os.remove(os.path.join(TEMP_DIR, AUDIO_FILE_NAME))

    silence_ranges = detect_silence_ranges(audio_segment, args.min_silence_len)
    complete_clip = VideoFileClip(args.input_filename)
    video_len = complete_clip.duration * 1000

    clips = []
    if len(silence_ranges) != 0:
        if not silence_ranges[0][0] == 0:
            clips.append(
                apply_speed_to_range(
                    complete_clip,
                    (0, silence_ranges[0][0] - 1),
                    args.speed_sound
                )
            )

        for i, silence_range in enumerate(silence_ranges):
            print(f'{i+1} of {len(silence_ranges)}\r', end='')
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

    concat_clip = concatenate_videoclips(clips, method='compose')
    concat_clip.write_videofile(args.output_filename)


if __name__ == '__main__':
    main()
