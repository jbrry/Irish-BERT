from transformers import RobertaConfig
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--out",
    default="./",
    type=str,
    help="Path to the output directory, where the files will be saved",
)
args = parser.parse_args()

config = RobertaConfig.from_pretrained("roberta-base", vocab_size=50265)
config.save_pretrained(f"./{args.out}")
