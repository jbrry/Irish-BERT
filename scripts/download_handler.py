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
            'oscar',
        },
        nargs='+',
    )
    return parser

def main(argv):
    args = argparser().parse_args(argv[1:])
    script_dir="./scripts/download_scripts/"

    for dataset in args.datasets:

        if dataset == "conll17":
            print("Downloading {} data.".format(dataset))
            
            cmd = script_dir + "download_{}_data.sh".format(dataset)
            rcmd = subprocess.call(cmd)

        elif dataset == "gdrive":
            print(f"Downloading {dataset} data.")

            cmd = script_dir + "download_{}_data.sh".format(dataset)
            rcmd = subprocess.call(cmd)

            # gather the various files into a common directory
            fcmd = "find data/ga/gdrive/ -maxdepth 3 -type f | python3 scripts/gather_gdrive_data_by_filelist.py"
            rcmd = subprocess.call(fcmd, shell=True)

        elif dataset == "oscar":
            print(f"Downloading {dataset} data.")

            cmd = script_dir + f"download_{dataset}_data.sh"
            rcmd = subprocess.call(cmd)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
