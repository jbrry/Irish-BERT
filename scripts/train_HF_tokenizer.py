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
    ap.add_argument('--min_freq', type=int, default=2,
                    help='Frequency threshold.')
    ap.add_argument('--vocab_size', type=int, default=30000,
                    help='Size of the vocabulary.')
    ap.add_argument('--limit_alphabet', type=int, default=1000,
                    help='Limit the size of the alphabet.')
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
        vocab_size=args.vocab_size,
        min_frequency=args.min_freq,
        show_progress=True,
        special_tokens=['[PAD]', '[UNK]', '[CLS]', '[SEP]', '[MASK]'],
        limit_alphabet=args.limit_alphabet,
        wordpieces_prefix="##"
    )

    # This will save the vocab as a json dictionary,
    # The vocab entries are located in ["model"]["vocab"]
    tokenizer.save(f"{args.outdir}/vocab.json", True)

    # read the json file back in to easily access
    # the vocabulary elements that interest us
    with open(f"{args.outdir}/vocab.json") as json_file:
        data = json.load(json_file)
        vocab = data["model"]["vocab"]
        # get list of all words (subword units) in the vocab
        words = []
        for w in vocab:
            assert vocab[w] == len(words)  # check index order
            words.append(w)
        json_file.close()

    # write vocab in the order found in the json file
    with open(f"{args.outdir}/vocab.txt", "w") as txt_file:
        for i, w in enumerate(words, start=1):
            txt_file.write(w + "\n")
            # most implementations write the first special symbol, then the unused entries
            if i == 1:
                for j in range(args.number_unused):
                    txt_file.write(f"[unused{j}]\n")

        txt_file.close()
        print(f"Finished writing vocabulary to {args.outdir}/vocab.txt")
    
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

