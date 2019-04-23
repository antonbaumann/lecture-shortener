import argparse
import os.path


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


def arguments():
    parser = argparse.ArgumentParser(description='Speed up lectures')
    parser.add_argument(
        '-i',
        dest='input_filename',
        required=True,
        help='input file path',
        metavar="INFILE",
        type=lambda x: validate_input_file(parser, x)
    )
    parser.add_argument(
        '-o',
        dest='input_filename',
        required=True,
        help='output file path',
        metavar='OUTFILE',
        type=lambda x: validate_output_file(parser, x)
    )
    parser.add_argument(
        '--speed-talking',
        type=float,
        default=1.6,
        help='general video speed',
    )
    parser.add_argument(
        '--speed-silence',
        type=float,
        default=5.0,
        help='video speed during silence',
    )
    parser.add_argument(
        '--silence-threshold',
        type=float,
        default=0.3,
        help='section will be labeled as silent if silence is longer than `silence_threshold`',
    )
    return parser.parse_args()


def main():
    args = arguments()


if __name__ == '__main__':
    main()
