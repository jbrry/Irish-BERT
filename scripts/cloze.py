# pip install transformers
from transformers import AutoModelWithLMHead, AutoTokenizer
import torch

# gaBERT
model_path = 'DCU-NLP/bert-base-irish-cased-v1'

# mBERT off shelf
# model_path = 'bert-base-multilingual-cased'

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelWithLMHead.from_pretrained(model_path)

# example masked sentences or read in from file
masked_lines_short = ["An [MASK] Eilís an bainisteoir?",
"Is [MASK] an líne glas teorainn an cheantair."]

for masked_line in masked_lines_short:

  input = tokenizer.encode(masked_line, return_tensors="pt")
  mask_token_index = torch.where(input == tokenizer.mask_token_id)[1]

  token_logits = model(input)[0]
  mask_token_logits = token_logits[0, mask_token_index, :]

  top_token = torch.topk(mask_token_logits, 1, dim=1).indices[0].tolist()
  print(masked_line.replace(tokenizer.mask_token, tokenizer.decode([top_token[0]])))

# top_5_tokens = torch.topk(mask_token_logits, 5, dim=1).indices[0].tolist()

 # for token in top_5_tokens:
 #   print(masked_line.replace(tokenizer.mask_token, tokenizer.decode([token])))