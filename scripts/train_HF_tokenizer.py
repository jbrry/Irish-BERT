import sys
import os
from tokenizers import BertWordPieceTokenizer

# Usage:
# python scripts/train_HF_tokenizer.py /path/to/ga_BERT/wiki-bert-pipeline/data/conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8/ga/filtered-concatenated/ga_filtered_all.txt vocabs

training_file = sys.argv[1]
outdir = sys.argv[2]

if not os.path.exists(outdir):
    print(f"Creating output directory: {outdir}")
    os.makedirs(outdir)

tokenizer = BertWordPieceTokenizer(
    clean_text=True, 
    handle_chinese_chars=False,
    strip_accents=False,
    lowercase=False, 
)

trainer = tokenizer.train( 
    training_file,
    vocab_size=30000,
    min_frequency=2,
    show_progress=True,
    special_tokens=['[PAD]', '[UNK]', '[CLS]', '[SEP]', '[MASK]'],
    limit_alphabet=1000,
    wordpieces_prefix="##"
)

# This will save the vocab as a json dictionary,
# The vocan entries are located in ["model"]["vocab"]
# You need to create a utility to extract the keys in this dictionary,
# e.g. just the text strings and save as 'vocab.txt'
tokenizer.save(f"{outdir}/vocab.json", True)