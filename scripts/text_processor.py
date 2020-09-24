import os
import re
import sys
import json
import random

import gzip
import bz2
from glob import glob

from tqdm import tqdm
import itertools
import logging

from pathlib import Path
from argparse import ArgumentParser

"""
Process raw text files before training BERT/
Sources: https://github.com/jbarrow/bert_from_scratch/blob/master/structurebert/initialize_original_tf_bert.py
         https://colab.research.google.com/drive/1nVn6AFpQSzXBt8_ywfx6XR8ZfQXlKGAz#scrollTo=0gngtEZWqVhY&forceEdit=true&sandboxMode=true
"""


def normalize_text(text, do_lower_case):
    if do_lower_case:
        # lowercase text
        text = str(text).lower()
    # remove non-UTF
    text = text.encode("utf-8", "ignore").decode()
    return text


def grouper(iterable, bucket_size):
    """
    Split data into fixed size buckets

    https://github.com/Helsinki-NLP/OpusFilter/blob/580d4aceb89eae64e31fe8a77c9ebc2a170d6cb8/opusfilter/__init__.py
    """
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, bucket_size))
        if not chunk:
            return
        yield chunk


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--datasets', type=str, help='Specify the datasets to download.',
        choices={
            'conll17',
            'gdrive',
            'oscar',
        }, nargs='+')
    parser.add_argument('--bucket-size', type=int, default=10000, help='How many lines to include in each outfile.')
    parser.add_argument('--do-lower-case', action='store_true')
    parser.add_argument('--encoding', default='utf-8')

    args = parser.parse_args()

    sentence_bucket = []
    for corpus in args.datasets:
        print(f"working on {corpus} ...")

        data_path = f"data/ga/{corpus}/raw"
        out_path = f"data/ga/{corpus}/processed"
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        
        for fn in os.listdir(data_path):
            file_path = os.path.join(data_path, fn)
            
            if fn.endswith('.bz2'):
                with bz2.open(file_path, 'rt', encoding=args.encoding, errors='ignore') as fi:
                    for i, l in enumerate(tqdm(fi)):
                        sentence_bucket.append(normalize_text(l, args.do_lower_case))
        
        print(f"found {len(sentence_bucket)} sentences in {corpus}")
        
        split_buckets = grouper(sentence_bucket, args.bucket_size)
        for i, split_bucket in enumerate(split_buckets):
            if i < 10:
                i = str(0) + str(i)
            else:
                i = str(i)

            outfile = out_path + '/' + corpus + "_" + i
            with open(outfile, 'w', encoding=args.encoding) as fo:
                for s in split_bucket:
                    fo.write(s)
