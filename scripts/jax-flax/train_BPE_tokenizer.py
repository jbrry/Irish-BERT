import argparse
import glob
from os.path import join

from tokenizers import ByteLevelBPETokenizer

parser = argparse.ArgumentParser()
parser.add_argument(
    "--files",
    default=None,
    metavar="path",
    type=str,
    required=True,
    help="The files to use as training; accept '**/*.txt' type of patterns \
                          if enclosed in quotes",
)
parser.add_argument(
    "--out",
    default="./",
    type=str,
    help="Path to the output directory, where the files will be saved",
)
args = parser.parse_args()

files = glob.glob(args.files)
if not files:
    print(f"File does not exist: {args.files}")
    exit(1)


# Initialize an empty tokenizer
tokenizer = ByteLevelBPETokenizer(add_prefix_space=True)

# Special tokens
BOS = "<s>"
EOS = "</s>"
UNK = "<unk>"
PAD = "<pad>"
MASK = "<mask>"

# And then train
tokenizer.train(
    files,
    vocab_size=50265,
    min_frequency=2,
    show_progress=True,
    special_tokens=[BOS, PAD, EOS, UNK, MASK],
)

# Save tokenizer
tokenizer.save(f"{args.out}/tokenizer.json")
