import sys
import os
import json

from tokenizers import BertWordPieceTokenizer

# Usage:
# python scripts/train_HF_tokenizer.py /path/to/ga_BERT/wiki-bert-pipeline/data/conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8/ga/filtered-concatenated/ga_filtered_all.txt vocabs

training_file = sys.argv[1]
outdir = sys.argv[2]
number_unused = int(sys.argv[3])

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
# The vocab entries are located in ["model"]["vocab"]
tokenizer.save(f"{outdir}/vocab.json", True)

with open(f"{outdir}/vocab.json") as json_file:
    data = json.load(json_file)
    vocab = data["model"]["vocab"]
    
    words = []
    for w in vocab:
        words.append(w)
    json_file.close()

with open(f"{outdir}/vocab.txt", "w") as txt_file:
    for i, w in enumerate(words, start=1):
        txt_file.write(w + "\n")
        # most implementations write the first special symbol, then the unused entries
        if i == 1:
            for j in range(number_unused):
                txt_file.write(f"[unused{j}]" + "\n")

    txt_file.close()
    print(f"Finished writing vocabulary to {outdir}/vocab.txt")

