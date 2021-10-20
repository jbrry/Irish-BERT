from transformers import pipeline
from transformers import GPT2LMHeadModel, GPT2Tokenizer

tokenizer = GPT2Tokenizer.from_pretrained("jbarry/irish-gpt2")

sample_lines=[
    "Ceoltóir Meiriceánach ab ea Johnny Cash",
    "Ba file é Oscar Wilde",
    "Tá Coláiste na Tríonóide lonnaithe i",
    'Ar ith sé an dinnéar?',
]

nlp = pipeline(
    "text-generation",
    model="jbarry/irish-gpt2",
    tokenizer=tokenizer
)

for i, prompt in enumerate(sample_lines):
    output = nlp(prompt)
    sequence = output[0]["generated_text"]
    print(f"Sequence {i}: {len(sequence.split())} tokens")
    print(sequence)
    print()
