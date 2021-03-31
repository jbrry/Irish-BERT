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
# You will need to download the model(s) from Google Drive and store it locally.
# Prepare symlinks in the `models` folder to match paths below or, if you do not
# plan to commit changes to the main repo, adjust `model_path` to your local
# directory containing the BERT model.
# Run: python scripts/inspect_lm_huggingface.py

"""
Based on the guide: https://huggingface.co/transformers/usage.html#masked-language-modeling

Some sample lines to try:
# TODO: Why curly brackets here but square brackets below?
masked_line=f"Is é an t-ábhar is fearr liom ná {MASK}"
masked_line=f"Tá Coláiste na Tríonóide lonnaithe i gcontae na {MASK}"
masked_line=f"Is {MASK} Éireannach é Oscar Wilde"
masked_line=f"Is é aigéaneolaíocht staidéar na {MASK}"
masked_line=f"Is é Deireadh Fómhair nó Mí Dheireadh Fómhair an {MASK} mí den bhliain"
masked_line=f"Ceoltóir {MASK} ab ea Johnny Cash"
"""

name2path = {
    'electra':   'models/ga_bert/output/pytorch/electra_base/',
    'gaelectra': 'models/ga_bert/output/pytorch/gabert-electra/conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8/',
    'gabert':    'models/ga_bert/output/pytorch/gabert/conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8',
    'mbert':     'models/multilingual_bert/output/pytorch/multi_cased_L-12_H-768_A-12/',
    'gambert':   'models/multilingual_bert/output/pytorch/???/',
}


def print_usage():
    print('Usage: %s [options] [FILENAME]' %(os.path.split(sys.argv[0])[-1]))
    print("""
Options:

    --model  NAME           What model to use, one of electra, gaelectra,
                            gabert, mbert and gambert
                            (Default: gabert)

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
    opt_do_lower_case = False
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
        elif option in ('--lc', '--do-lower-case'):
            opt_do_lower_case = True
        elif option in ('--from', '--read-from'):
            masked_lines = line_reader(sys.argv[1])
            del sys.argv[1]
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
    model_path = os.path.abspath(name2path[opt_model_name])

    if opt_use_pipeline:
        # Usage case 1: Huggingface pipeline module
        nlp = pipeline(
            "fill-mask",
            model = model_path,
        )
        tokeniser = BertTokenizer.from_pretrained(model_path, do_lower_case=opt_do_lower_case)
    else:
        tokeniser = AutoTokenizer.from_pretrained(model_path, do_lower_case=opt_do_lower_case)
        model = AutoModelWithLMHead.from_pretrained(model_path)
    assert '[MASK]' == tokeniser.mask_token
    for masked_line in masked_lines:
        #if opt_use_pipeline:
        for mask_multiplier in range(1, 1+opt_max_masks):
            print('multiplier', mask_multiplier)
            multi_mask = mask_multiplier * '[MASK]'
            multi_masked_line = masked_line.replace('[MASK]', multi_mask)
            print(multi_masked_line)
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
            print("\n")
        # else:
        #    raise NotImplementedError

if __name__ == '__main__':
    main()

