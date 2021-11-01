import os
import sys
import random

from tqdm import tqdm
from argparse import ArgumentParser

def argparser():
    parser = ArgumentParser(
        description='Merge text files and create train/valid/test files.'
    )
    parser.add_argument('--dataset-dir', type=str,
        help='Directory containing the files you want to merge.')
    parser.add_argument('--output-dir', type=str,
        help='Directory to write out files.')
    parser.add_argument('-r', '--ratios', type=float, nargs='+',
        default=[0.7, 0.15, 0.15],
        help="Train, valid and test ratios: e.g. 0.7, 0.15, 0.15")
    parser.add_argument('--encoding', default='utf-8')
    parser.add_argument('--random-seed', default=230)
    parser.add_argument('--do-shuffle', action='store_true')
    parser.add_argument('--pass-empty', action='store_true')
    
    return parser


def write_file(sentences, filename):
    print(f"writing {len(sentences)} to {filename}")
    
    with open(filename, 'w', encoding="utf-8") as fo:
        for s in sentences:
            fo.write(s)

def main(argv):
    args = argparser().parse_args(argv[1:])

    print(f"passing empty lines: {args.pass_empty}")
    assert sum(args.ratios) == 1, "Train, valid and test ratios must sum to 1"

    if not os.path.exists(args.output_dir):
        print(f"Creating output directory {args.output_dir}")
        os.makedirs(args.output_dir)

    sentence_bucket = []
    for fn in os.listdir(args.dataset_dir):
        file_path = os.path.join(args.dataset_dir, fn)
        with open(file_path, 'rt', encoding=args.encoding, errors='ignore') as fi:
            for l in tqdm(fi):
                # don't append empty lines by default
                if args.pass_empty:
                    sentence_bucket.append(l)
                else:
                    if len(l) > 0 and not l.isspace():
                        sentence_bucket.append(l)
        
        if args.pass_empty:
            # Create empty line as document boundary.
            sentence_bucket.append("\n")
    print(f"found {len(sentence_bucket)} sentences")

    random.seed(args.random_seed)   
    if args.do_shuffle:
        print("Shuffling input data")
        random.shuffle(sentence_bucket)

    train_ratio = args.ratios[0]
    valid_ratio = args.ratios[1] + train_ratio
    # the test portion will be the slice after the validation portion
    # so we don't actually need the rest_ratio.

    # train
    train_stride = int(train_ratio * len(sentence_bucket))
    train_sentences = sentence_bucket[:train_stride]
    train_file = os.path.join(args.output_dir, "train.txt")
    train_out = write_file(train_sentences, train_file)
    
    # valid
    valid_stride = int(valid_ratio * len(sentence_bucket))
    valid_sentences = sentence_bucket[train_stride:valid_stride]
    valid_file = os.path.join(args.output_dir, "valid.txt")
    valid_out = write_file(valid_sentences, valid_file)

    # test
    test_sentences = sentence_bucket[valid_stride:]
    # we might not always choose to have a test file.
    if len(test_sentences) > 0:
        test_file = os.path.join(args.output_dir, "test.txt")
        test_out = write_file(test_sentences, test_file)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
