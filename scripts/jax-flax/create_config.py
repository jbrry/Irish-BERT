from transformers import RobertaConfig

config = RobertaConfig.from_pretrained("roberta-base", vocab_size=50265)
config.save_pretrained("./irish-roberta-base")
