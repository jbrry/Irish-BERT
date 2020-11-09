"""
Filter specified datasets/corpora.

Usage: python3 scripts/filter_corpora.py --datasets <dataset(s)>

Requires running scripts/text_processor.py first.

"""
import sys
import subprocess
from argparse import ArgumentParser

def argparser():
    parser = ArgumentParser(
        description='Filter corpora using OpusFilter.'
    )
    parser.add_argument(
        '--datasets',
        type=str,
        help='Specify the datasets to download.',
        choices={
            'conll17',
            'gdrive',
            'NCI',
            'oscar',
        },
        nargs='+',
    )
    parser.add_argument('--filter-threshold', type=str,
        choices={
            '0',
            '05',
            '1',
            })

    return parser

def main(argv):
    args = argparser().parse_args(argv[1:])
    config_dir="configs/opusfilter/"

    for dataset in args.datasets:
        print(f"Filtering {dataset} data.")
        cfg = config_dir + "filter_{}_{}.yaml".format(dataset, args.filter_threshold)
        cmd = f"opusfilter {cfg}"
        rcmd = subprocess.call(cmd, shell=True)

if __name__ == '__main__':
    sys.exit(main(sys.argv))