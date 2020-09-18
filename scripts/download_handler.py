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
    script_dir="./scripts/"

    for dataset in args.datasets:

        if dataset == "conll17":
            print("Downloading {} data.".format(dataset))
            
            cmd = script_dir + "download_{}_data.sh".format(dataset)
            rcmd = subprocess.call(cmd)

        elif dataset == "gdrive":
            print("Downloading {} data.".format(dataset))

            cmd = script_dir + "download_{}_data.sh".format(dataset)
            rcmd = subprocess.call(cmd)

            # gather the various files into a common directory
            fcmd = "find data/ga/gdrive/ -maxdepth 3 -type f | python scripts/gather_gdrive_data.py"
            rcmd = subprocess.call(fc, shell=True)

        elif dataset == "oscar":
            print("Downloading {} data.".format(dataset))

            cmd = script_dir + "download_{}_data.sh".format(dataset)
            rcmd = subprocess.call(cmd)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
