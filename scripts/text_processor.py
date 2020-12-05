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
import subprocess

from pathlib import Path
from argparse import ArgumentParser

"""
Process raw text files before training BERT/
Sources: https://github.com/jbarrow/bert_from_scratch/blob/master/structurebert/initialize_original_tf_bert.py
         https://colab.research.google.com/drive/1nVn6AFpQSzXBt8_ywfx6XR8ZfQXlKGAz#scrollTo=0gngtEZWqVhY&forceEdit=true&sandboxMode=true

Usage:
    python scripts/text_processor.py --datasets conll17 gdrive NCI oscar --bucket-size 100000 --input-type raw --output-type processed
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
            'NCI',
            'NCI_old',
            'oscar',
        }, nargs='+')
    parser.add_argument('--bucket-size', type=int, default=100000,
    help='How many lines to include in each outfile. If you want to just have 1 file, specify a bucket size larger than the number of lines.')
    parser.add_argument('--do-lower-case', action='store_true')
    #parser.add_argument('--process-filtered', action='store_true')
    parser.add_argument('--encoding', default='utf-8')
    parser.add_argument('--input-type', type=str,
        choices={
            'raw',
            'processed',
            'filtered',
            })
    parser.add_argument('--output-type', type=str,
        choices={
            'raw',
            'processed',
            'filtered',
            })
    parser.add_argument('--filter-type', type=str, # all filtering will be done in wikibert
        choices={
            'basic',
            '0.5',
            '0.8',
            })

    args = parser.parse_args()
    
    
    for corpus in args.datasets:
        print(f"working on {corpus} ...")

        # create an empty bucket for each corpus
        sentence_bucket = []

        data_path = f"data/ga/{corpus}/{args.input_type}"
        out_path = f"data/ga/{corpus}/{args.output_type}"

        if not os.path.exists(out_path):
            os.makedirs(out_path)
        
        for fn in os.listdir(data_path):
            file_path = os.path.join(data_path, fn)

            if fn.endswith('.bz2'):
                with bz2.open(file_path, 'rt', encoding=args.encoding, errors='ignore') as fi:
                    for i, l in enumerate(tqdm(fi)):
                        sentence_bucket.append(normalize_text(l, args.do_lower_case))

            elif fn.endswith('.gz'):
                with gzip.open(file_path, 'rt', encoding=args.encoding, errors='ignore') as fi:
                    for i, l in enumerate(tqdm(fi)):
                        sentence_bucket.append(normalize_text(l, args.do_lower_case))

            elif fn.endswith('.txt'):
                with open(file_path, 'rt', encoding=args.encoding, errors='ignore') as fi:
                    for i, l in enumerate(tqdm(fi)):
                        sentence_bucket.append(normalize_text(l, args.do_lower_case))
            
        print(f"found {len(sentence_bucket)} sentences in {corpus}")
        
        split_buckets = grouper(sentence_bucket, args.bucket_size)
        for i, split_bucket in enumerate(split_buckets):
            outfile = f'{out_path}/{corpus}_{i:02d}'
            with open(outfile, 'w', encoding=args.encoding) as fo:
                for s in split_bucket:
                    fo.write(s)
            
            # compress file
            subprocess.call(f'bzip2 {outfile}', shell=True)
