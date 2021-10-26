import argparse
import glob
from os.path import join

from tokenizers import normalizers, pre_tokenizers, processors, Tokenizer, models, decoders, trainers

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
parser.add_argument(
    "--name", default="bytelevel-bpe", type=str, help="The name of the output vocab files"
)
args = parser.parse_args()

files = glob.glob(args.files)
if not files:
    print(f"File does not exist: {args.files}")
    exit(1)


# Special tokens
BOS = "<s>"
EOS = "</s>"
UNK = "<unk>"
PAD = "<pad>"
MASK = "<mask>"

# Build a tokenizer
tokenizer = Tokenizer(models.BPE())
tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
tokenizer.decoder = decoders.ByteLevel()

# Build a trainer
trainer = trainers.BpeTrainer(
    vocab_size=30000,
    special_tokens=[BOS, PAD, EOS, UNK, MASK],
    initial_alphabet=pre_tokenizers.ByteLevel.alphabet()
)

# Train
tokenizer.train(
    files,
    trainer=trainer,
)

# Attach the Roberta Processing (https://github.com/huggingface/tokenizers/issues/640)
tokenizer.post_processor = processors.RobertaProcessing(
    sep=(EOS, tokenizer.token_to_id(EOS)),
    cls=(BOS, tokenizer.token_to_id(BOS))
)

# Save tokenizer
tokenizer.save(f"{args.out}/tokenizer.json")

# Sanity check
import transformers
from transformers import RobertaTokenizerFast
tok = RobertaTokenizerFast(tokenizer_file=f"{args.out}/tokenizer.json")

