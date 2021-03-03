from transformers import pipeline
from transformers import AutoModelForMaskedLM, AutoTokenizer
import torch

# Usage:
# Requires `transformers` library: `pip install transformers`
# You will need to download the model from Google Drive and store it locally.
# Adjust `bert_path` to your local directory containing the BERT model.
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

bert_path = "/home/jbarry/spinning-storage/jbarry/ga_BERT/Irish-BERT/models/ga_bert/output/pytorch_models/conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8/"

# Usage case 1: Pipelines
nlp = pipeline(
    "fill-mask",
    model=bert_path,
)

MASK = nlp.tokenizer.mask_token
masked_line=f"Ceoltóir {MASK} ab ea Johnny Cash"

print(f"Trying sample sentence: {masked_line}")
outputs = nlp(masked_line)
top_k = 5

for output in outputs[:top_k]:
    print(f"Token: {output['token_str']}, score: {output['score']}, id: {output['token']}")

# Usage case 2: Using the model directly
tokenizer = AutoTokenizer.from_pretrained(bert_path)
model = AutoModelForMaskedLM.from_pretrained(bert_path)

masked_line=f"Tá Coláiste na Tríonóide lonnaithe i gcontae na {MASK}"

input = tokenizer.encode(masked_line, return_tensors="pt")
mask_token_index = torch.where(input == tokenizer.mask_token_id)[1]

token_logits = model(input)[0]
mask_token_logits = token_logits[0, mask_token_index, :]

top_5_tokens = torch.topk(mask_token_logits, 5, dim=1).indices[0].tolist()

for token in top_5_tokens:
    print(masked_line.replace(tokenizer.mask_token, tokenizer.decode([token])))