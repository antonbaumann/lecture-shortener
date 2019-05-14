#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess

from audiotsm import phasevocoder
from audiotsm.io.array import ArrayReader, ArrayWriter
from scipy.io import wavfile

from lecture_shortener import globals


# get sample rate and audio data from video file
def get_audio_data(video_file_path, threads=1) -> (int, list):
    extract_audio_from_video(video_file_path, threads)
    sample_rate, audio_data = wavfile.read(os.path.join(globals.TEMP_DIR, globals.AUDIO_FILE_NAME))
    os.remove(os.path.join(globals.TEMP_DIR, globals.AUDIO_FILE_NAME))
    return sample_rate, audio_data


# converts a video file into a wav file and saves it to TEMP_DIR/AUDIO_FILE_NAME
def extract_audio_from_video(video_file, threads=1):
    print('[i] extracting audio from video ...')
    if not os.path.exists(globals.TEMP_DIR):
        os.mkdir(globals.TEMP_DIR)
    command = f'ffmpeg -i {video_file} -ab 160k -ac 2 -ar 44100 -threads {threads} ' \
        f'-vn {os.path.join(globals.TEMP_DIR, globals.AUDIO_FILE_NAME)} -y'
    subprocess.call(command, shell=True, stdout=globals.DEVNULL)
    print('[✓] done!\n')


def apply_speed_to_audio(audio, speed):
    reader = ArrayReader(audio)
    writer = ArrayWriter(2)
    tsm = phasevocoder(reader.channels, speed)
    tsm.run(reader, writer)
    return writer.data
