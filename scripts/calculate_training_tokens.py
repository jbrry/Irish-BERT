"""Calculates how many epochs a model runs for over a corpus."""

def epoch_calculator(name, batch_size, seq_len, steps, corpus_size):
    """
    Args:
        name: name of model.
        batch_size: the batch size used by the model.
        seq_len: the number of tokens in each training sequence.
        steps: the number of steps the model has been ran for.
        corpus_size: the size of the training corpus in words.
    """

    tokens_per_batch = (batch_size * seq_len)
    total = tokens_per_batch * steps
    epochs = total / corpus_size

    print(f"{name} with {steps} steps, batch size {batch_size} and seq len: {seq_len}\n"
        f"Tokens seen: {total/1000000}M"
        f" Approx. {epochs:.2f} epochs over a corpus size of {corpus_size/1000000:.2f}M tokens.\n")
        

# Original BERT paper
name = "BERT"
corpus_size = 3300000000
seq_len = 128
batch_size = 256
steps = 900000
epochs = epoch_calculator(name, batch_size, seq_len, steps, corpus_size)

# Original BERT paper
name = "BERT"
corpus_size = 3300000000
seq_len = 512
batch_size = 256
steps = 100000
epochs = epoch_calculator(name, batch_size, seq_len, steps, corpus_size)

# GaBERT-base
name = "GaBERT-base"
corpus_size = 159429404 # cat ga/filtered-texts/* | wc = 7937938 159429404 919788128
seq_len = 128
batch_size = 32
steps = 900000
epochs = epoch_calculator(name, batch_size, seq_len, steps, corpus_size)

# GaBERT-base
name = "GaBERT-base"
corpus_size = 159429404 # cat ga/filtered-texts/* | wc = 7937938 159429404 919788128
seq_len = 512
batch_size = 64
steps = 100000
epochs = epoch_calculator(name, batch_size, seq_len, steps, corpus_size)

# GaELECTRA-base
name = "GaELECTRA-base"
corpus_size = 159429404
seq_len = 512
batch_size = 256
steps = 50000
epochs = epoch_calculator(name, batch_size, seq_len, steps, corpus_size)