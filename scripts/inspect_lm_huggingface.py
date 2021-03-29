#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) 2021 Dublin City University
# All rights reserved. This material may not be
# reproduced, displayed, modified or distributed without the express prior
# written permission of the copyright holder.

import os
from transformers import pipeline
from transformers import AutoModelForMaskedLM, AutoTokenizer
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
    'gabert':    'models/ga_bert/output/pytorch/gabert/pytorch/',
    'mbert':     'models/multilingual_bert/output/pytorch/multi_cased_L-12_H-768_A-12/',
    'gambert':   'models/multilingual_bert/output/pytorch/???/',
}

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

def main():
    opt_model_name   = 'gabert'
    opt_use_pipeline = True
    opt_top_k        = 5
    opt_output_tsv   = False
    # TODO: process command line options
    model_path = os.path.abspath(name2path[opt_model_name])
    if opt_use_pipeline:
        # Usage case 1: Huggingface pipeline module
        nlp = pipeline(
            "fill-mask",
            model = model_path,
        )
        assert '[MASK]' == nlp.tokenizer.mask_token
    else:
        raise NotImplementedError
    for masked_line in masked_lines:
        print(masked_line)
        if opt_use_pipeline:
            outputs = nlp(masked_line)
            if opt_output_tsv:
                print('Rank\tToken\tScore\tID')
            for index, output in enumerate(outputs[:opt_top_k]):
                rank = index + 1
                if opt_output_tsv:
                    print(f"{rank}\t{output['token_str']}\t{output['score']}\t{output['token']}")
                else:
                    print(f"Token: {output['token_str']}, score: {output['score']}, id: {output['token']}")
            print("\n")
        else:
            raise NotImplementedError

if __name__ == '__main__':
    main()

