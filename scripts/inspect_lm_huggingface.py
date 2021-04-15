#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) 2021 Dublin City University
# All rights reserved. This material may not be
# reproduced, displayed, modified or distributed without the express prior
# written permission of the copyright holder.

import os
import sys
from transformers import pipeline
from transformers import AutoModelForMaskedLM, AutoTokenizer
from transformers import AutoModelWithLMHead
from transformers import BertTokenizer
import torch

# Python 3

# Usage:
# Requires `transformers` library: `pip install transformers`
# Run: python scripts/inspect_lm_huggingface.py --help

# Based on the guide: https://huggingface.co/transformers/usage.html#masked-language-modeling

name2path = {
    # You will need to download the model(s) from Google Drive and store it locally.
    # If you have not enough space under 'models/' use a symlink to point to your
    # alternative location.
    # mbert can be downloaded from the bert github page.
    # If your download is missing a tokeniser configuration you can find a suitable
    # on in 'models/ga_bert/'.
    'electra':   ('local', 'models/ga_bert/output/pytorch/electra_base/',),
    'gaelectra': ('local', 'models/ga_bert/output/pytorch/gabert-electra/conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8/',),
    'gabert':    ('local', 'models/ga_bert/output/pytorch/gabert/conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8',),
    'mbert':     ('repo',  'bert-base-multilingual-cased',),
    'mbertdl':   ('local', 'models/multilingual_bert/output/pytorch/multi_cased_L-12_H-768_A-12/',),
    'gambert':   ('local', 'models/multilingual_bert/output/pytorch/???/',),
    'wikibert':  ('repo',  'TurkuNLP/wikibert-base-ga-cased',),
    'wikibertdl': ('local',  'models/TurkuNLP/wikibert-base-ga-cased',),
}

def print_usage():
    print('Usage: %s [options] [FILENAME]' %(os.path.split(sys.argv[0])[-1]))
    print("""
Options:

    --model  NAME           What model to use, one of electra, gaelectra,
                            gabert, mbert, gambert and wikibert, and, for
                            local mbert/wikibert copies, mbertdl and
                            wikibertdl
                            (Default: gabert)

                            Warning: At the time of writing, the wikibert
                            model is missing the "do_lower_case": false
                            configuration file for the tokeniser.

    --top  NUMBER           How many top predictions to output
                            (Default: 5)

    --tsv                   Produce tab-separated output
                            (Default: repeat descriptions)

    --from  FILENAME        Read input lines from first column of file,
                            - = stdin
                            If this is the last option `--from` can be
                            omitted.
                            (Default: process hard-coded lines)

    --multi-mask  NUMBER    Also make predictions for inputs with up to
                            NUMBER copies of [MASK].
                            At the time of writing not supported by the
                            underlying library.
                            (Default: 1 = no extra copies)

    --no-subwords           Do not print subword tokenisation of input.
                            (Default: show python list of subword tokens)

    --help                  Show this message
""")

masked_lines=[
    "Is é Deireadh Fómhair an [MASK] mí den bhliain.",
    "Ceoltóir [MASK] ab ea Johnny Cash.",
    "Ba [MASK] é Oscar Wilde.",
    "Tá Coláiste na Tríonóide lonnaithe i [MASK].",
    "Tá Coláiste na Tríonóide lonnaithe i gContae [MASK].",
    "Tá Coláiste na Tríonóide lonnaithe i gContae [MASK] Átha Cliath.",
    "Tá Coláiste na Tríonóide lonnaithe i lár na [MASK].",
    "Is í an [MASK] an t-ábhar is fearr liom.",
    "[MASK] an dath is fearr liom.",
    'Ar ith [MASK] an dinnéar?',
    'ar ith [MASK] an dinnear?',
    'Dúirt sé [MASK] múinteoir é.',
    'duirt se [MASK] muinteoir e.',
]

def line_reader(filename):
    if filename == '-':
        f = sys.stdin
    else:
        f = open(filename, 'r')
    while True:
        line = f.readline()
        if not line:
            break
        yield line.split('\t')[0].rstrip()
    if filename != '-':
        f.close()

def main():
    global masked_lines
    opt_model_name   = 'gabert'
    opt_use_pipeline = True
    opt_top_k        = 5
    # opt_max_masks > 1 currently not supported by huggingface:
    # https://github.com/huggingface/transformers/issues/3619
    opt_max_masks    = 1
    opt_output_tsv   = False
    opt_print_subwords = True
    opt_help    = False
    opt_debug   = False
    opt_verbose = False
    # process command line options
    while len(sys.argv) >= 2 and sys.argv[1][:1] == '-':
        option = sys.argv[1]
        option = option.replace('_', '-')
        del sys.argv[1]
        if option in ('--help', '-h'):
            opt_help = True
            break
        elif option in ('--model', '--model-name'):
            opt_model_name = sys.argv[1]
            del sys.argv[1]
        elif option in ('--top', '--top-k'):
            opt_top_k = int(sys.argv[1])
            del sys.argv[1]
        elif option in ('--multi-mask', '--max-masks'):
            opt_max_masks = int(sys.argv[1])
            del sys.argv[1]
        elif option in ('--tsv', '--output-tsv'):
            opt_output_tsv = True
        elif option in ('--from', '--read-from'):
            masked_lines = line_reader(sys.argv[1])
            del sys.argv[1]
        elif option in ('--no-subwords', '--do-not-print-subwords'):
            opt_print_subwords = False
        elif option == '--debug':
            opt_debug = True
        elif option == '--verbose':
            opt_verbose = True
        else:
            print('Unsupported option %s' %option)
            opt_help = True
            break
    if len(sys.argv) not in (1,2):
        opt_help = True
    if opt_help:
        print_usage()
        sys.exit(0)
    if len(sys.argv) == 2:
        # FILENAME without "--from"
        masked_lines = line_reader(sys.argv[1])
    # prepare model
    model_type, model_path_or_name = name2path[opt_model_name]
    if model_type == 'local':
        model_path_or_name = os.path.abspath(model_path_or_name)
        if not os.path.exists(os.path.join(model_path_or_name, 'tokenizer_config.json')):
            raise ValueError('Model is missing tokenizer_config.json')
    elif model_type == 'repo':
        pass
    else:
        raise ValueError('unknown model type in hard-coded configuration for %s' %opt_model_name)
    if opt_use_pipeline:
        # Usage case 1: Huggingface pipeline module
        nlp = pipeline(
            "fill-mask",
            model = model_path_or_name,
        )
        tokeniser = nlp.tokenizer
    else:
        tokeniser = AutoTokenizer.from_pretrained(model_path_or_name)
        model = AutoModelWithLMHead.from_pretrained(model_path_or_name)
    assert '[MASK]' == tokeniser.mask_token
    for masked_line in masked_lines:
        #if opt_use_pipeline:
        for mask_multiplier in range(1, 1+opt_max_masks):
            #print('multiplier', mask_multiplier)
            multi_mask = mask_multiplier * '[MASK]'
            multi_masked_line = masked_line.replace('[MASK]', multi_mask)
            print(multi_masked_line)
            if opt_print_subwords:
                encoded = tokeniser(multi_masked_line)
                print(tokeniser.convert_ids_to_tokens(encoded['input_ids']))
            if not '[MASK]' in masked_line:
                break
            outputs = nlp(multi_masked_line)
            if opt_output_tsv:
                print('Rank\tToken\tScore\tID')
            for index, output in enumerate(outputs[:opt_top_k]):
                rank = index + 1
                if opt_output_tsv:
                    print(f"{rank}\t{output['token_str']}\t{output['score']}\t{output['token']}")
                else:
                    print(f"Token: {output['token_str']}, score: {output['score']}, id: {output['token']}")
            print()
        # else:
        #    raise NotImplementedError

if __name__ == '__main__':
    main()

