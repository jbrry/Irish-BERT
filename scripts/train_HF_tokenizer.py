import sys
import os
import json

from tokenizers import BertWordPieceTokenizer


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument('--outdir', type=str,
                    help='Where to write output.')
    ap.add_argument('--number_unused', type=int,
                    help='Number of unused entries to write.')
    ap.add_argument('file', nargs='+')
    return ap


def main(argv):
    args = argparser().parse_args(argv[1:])

    if not os.path.exists(args.outdir):
        print(f"Creating output directory: {args.outdir}")
        os.makedirs(args.outdir)

    tokenizer = BertWordPieceTokenizer(
        clean_text=True,
        handle_chinese_chars=False,
        strip_accents=False,
        lowercase=False, 
    )

    training_file = args.file

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
    tokenizer.save(f"{args.outdir}/vocab.json", True)

    with open(f"{args.outdir}/vocab.json") as json_file:
        data = json.load(json_file)
        vocab = data["model"]["vocab"]
        
        words = []
        for w in vocab:
            words.append(w)
        json_file.close()

    with open(f"{args.outdir}/vocab.txt", "w") as txt_file:
        for i, w in enumerate(words, start=1):
            txt_file.write(w + "\n")
            # most implementations write the first special symbol, then the unused entries
            if i == 1:
                for j in range(args.number_unused):
                    txt_file.write(f"[unused{j}]" + "\n")

        txt_file.close()
        print(f"Finished writing vocabulary to {args.outdir}/vocab.txt")
    
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

