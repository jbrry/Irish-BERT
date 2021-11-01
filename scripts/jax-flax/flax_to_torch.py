import argparse
import glob
from os.path import join

parser = argparse.ArgumentParser()
parser.add_argument(
    "--model-path",
    default=None,
    metavar="path",
    type=str,
    required=True,
    help="The path to the pretrained Flax model.",
)
parser.add_argument(
    "--out",
    default=None,
    type=str,
    help="Path to the output directory, where the files will be saved",
)
parser.add_argument(
    "--model-type",
    default="roberta",
    choices=["roberta","gpt2"],
    type=str,
    help="Type of model.",
)
args = parser.parse_args()

model_path = glob.glob(args.model_path).pop()
if not model_path:
    print(f"Model path does not exist: {args.model_path}")
    exit(1)

if args.out is None:
    args.out = model_path

if args.model_type == "roberta":
    from transformers import RobertaForMaskedLM, AutoTokenizer

    model = RobertaForMaskedLM.from_pretrained(f"{model_path}", from_flax=True)
    model.save_pretrained(f"{args.out}")
    tokenizer = AutoTokenizer.from_pretrained(f"{model_path}")
    tokenizer.save_pretrained(f"{args.out}")

elif args.model_type== "gpt2":
    from transformers import GPT2LMHeadModel

    model = GPT2LMHeadModel.from_pretrained(model, from_flax=True)
    model.save_pretrained(f"{args.out}")
