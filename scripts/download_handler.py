"""
Download specified datasets/corpora.

Usage: python3 scripts/download_handler.py --datasets <dataset(s)>
E.g. python3 scripts/download_handler.py --datasets gdrive

"""
import sys
import subprocess
from argparse import ArgumentParser

def argparser():
    
    parser = ArgumentParser(
        description='Data download handler.'
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
            'paracrawl',
            'sampleNCI',
        },
        nargs='+',
    )
    return parser

def main(argv):
    args = argparser().parse_args(argv[1:])
    script_dir="./scripts/download_scripts/"

    for dataset in args.datasets:

        if dataset in ("conll17", "NCI", "oscar", "paracrawl", "sampleNCI"):
            print(f"Downloading {dataset} data.")
            cmd = script_dir + f"download_{dataset}_data.sh"
            rcmd = subprocess.call(cmd)

        elif dataset == "gdrive":
            print(f"Downloading {dataset} data.")
            # download all files from gdrive
            cmd = script_dir + f"download_{dataset}_data.sh"
            rcmd = subprocess.call(cmd, shell=True)

            # gather the various files into a common directory
            fcmd = "find data/ga/gdrive/ -maxdepth 3 -type f | python3 scripts/gather_gdrive_data_by_filelist.py"
            rcmd = subprocess.call(fcmd, shell=True)

        else:
            raise ValueError('Missing code for dataset %r' %dataset)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
