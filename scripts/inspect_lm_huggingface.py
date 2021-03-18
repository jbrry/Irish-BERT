from transformers import pipeline
from transformers import AutoModelForMaskedLM, AutoTokenizer
import torch

# Usage:
# Requires `transformers` library: `pip install transformers`
# You will need to download the model(s) from Google Drive and store it locally.
# Adjust `model_path` to your local directory containing the BERT model.
# To run: python scripts/inspect_lm_huggingface.py

"""
Based on the guide: https://huggingface.co/transformers/usage.html#masked-language-modeling

Some sample lines to try:
masked_line=f"Is é an t-ábhar is fearr liom ná {MASK}"
masked_line=f"Tá Coláiste na Tríonóide lonnaithe i gcontae na {MASK}"
masked_line=f"Is {MASK} Éireannach é Oscar Wilde"
masked_line=f"Is é aigéaneolaíocht staidéar na {MASK}"
masked_line=f"Is é Deireadh Fómhair nó Mí Dheireadh Fómhair an {MASK} mí den bhliain"
masked_line=f"Ceoltóir {MASK} ab ea Johnny Cash"
"""

#model_path = "/home/jbarry/ga_BERT/Irish-BERT/models/ga_bert/output/pytorch/electra_base/"
model_path = "/home/jbarry/ga_BERT/Irish-BERT/models/ga_bert/output/pytorch/gabert-electra/conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8/"

# Usage case 1: Pipelines
nlp = pipeline(
    "fill-mask",
    model=model_path,
)

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

for masked_line in masked_lines:
    print(f"{masked_line}")
    outputs = nlp(masked_line)
    top_k = 5

    for output in outputs[:top_k]:
        print(f"Token: {output['token_str']}, score: {output['score']}, id: {output['token']}")
    print("\n")


