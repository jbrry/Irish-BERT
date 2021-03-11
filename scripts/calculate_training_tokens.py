
def epoch_calculator(name, batch_size, seq_len, steps, corpus_size, steps_proportion):

    tokens_per_batch = (batch_size * seq_len)
    total = tokens_per_batch * steps
    epochs = total / corpus_size

    print(f"{name} {steps_proportion}% @ {seq_len}: Tokens seen: {total/1000000}M, Approx. {epochs:.2f} epochs.")

# Original BERT paper
name = "BERT"
corpus_size = 3300000000
seq_len = 128
batch_size = 256
steps = 900000
steps_proportion = 90
epochs = epoch_calculator(name, batch_size, seq_len, steps, corpus_size, steps_proportion)

# Original BERT paper
name = "BERT"
corpus_size = 3300000000
seq_len = 512
batch_size = 256
steps = 100000
steps_proportion = 10
epochs = epoch_calculator(name, batch_size, seq_len, steps, corpus_size, steps_proportion)

# GaBERT-base
name = "GaBERT-base"
corpus_size = 159429404 # cat ga/filtered-texts/* | wc = 7937938 159429404 919788128
seq_len = 128
batch_size = 64
steps = 900000
steps_proportion = 90
epochs = epoch_calculator(name, batch_size, seq_len, steps, corpus_size, steps_proportion)

# GaBERT-base
name = "GaBERT-base"
corpus_size = 159429404 # cat ga/filtered-texts/* | wc = 7937938 159429404 919788128
seq_len = 512
batch_size = 64
steps = 100000
steps_proportion = 10
epochs = epoch_calculator(name, batch_size, seq_len, steps, corpus_size, steps_proportion)

# GaELECTRA-base
name = "GaELECTRA-base"
corpus_size = 159429404
seq_len = 512
batch_size = 256
steps = 250000
steps_proportion = 100
epochs = epoch_calculator(name, batch_size, seq_len, steps, corpus_size, steps_proportion)