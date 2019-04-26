#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time


def time_remaining(iteration, total_iterations, start):
    iterations_per_sec = (iteration + 1) / (time.time() - start)
    return (total_iterations - (iteration + 1)) / iterations_per_sec


def format_seconds(seconds):
    ret = ''
    minutes = int(seconds / 60)
    hours = minutes // 60
    if hours != 0:
        ret += f'{hours}h'
    if hours != 0 or minutes % 60 != 0:
        ret += f' {minutes}m '
    ret += f'{int(seconds % 60)}s'
    return ret


def show_saved_time_info(ranges):
    saved_time = 0
    print('[i] silence ranges:')
    for range in ranges:
        saved_time += range[1] - range[0]
        print(f'    {range}')

    print()
    print(f'[i] saved time: {format_seconds(saved_time)}')
