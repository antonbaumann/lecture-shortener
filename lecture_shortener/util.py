#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import time


def time_remaining(iteration, total_iterations, start) -> float:
    delta = time.time() - start
    if delta == 0:
        delta = 1
    iterations_per_sec = (iteration + 1) / delta
    return (total_iterations - (iteration + 1)) / iterations_per_sec


def format_seconds(seconds) -> str:
    ret = ''
    minutes = int(seconds / 60)
    hours = minutes // 60
    if hours != 0:
        ret += f'{hours}h'
    if hours != 0 or minutes % 60 != 0:
        ret += f' {minutes % 60}m '
    ret += f'{int(seconds % 60)}s'
    return ret


def show_saved_time_info(ranges):
    saved_time = 0
    print('[i] silence_detection ranges:')
    for range in ranges:
        saved_time += range[1] - range[0]
        print(f'    {range}')

    print()
    print(f'[i] saved time: {format_seconds(saved_time)}')


def clear_dir(folder, only_files=True):
    for element in os.listdir(folder):
        element_path = os.path.join(folder, element)
        try:
            if os.path.isfile(element_path):
                os.unlink(element_path)
            elif os.path.isdir(element_path) and not only_files:
                shutil.rmtree(element_path)
        except Exception as e:
            print(e)
