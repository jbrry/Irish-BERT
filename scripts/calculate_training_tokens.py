
def epoch_calculator(name, batch_size, max_seq_len, steps, corpus_size):

    tokens_per_batch = (batch_size * max_seq_len)
    total = tokens_per_batch * steps
    epochs = total / corpus_size

    print(f"{name}: Tokens seen: {total}, Approx. {epochs:.2f} epochs.")


# Original BERT paper
name = "BERT"
corpus_size = 3300000000
max_seq_len = 512
batch_size = 256
steps = 1000000
epochs = epoch_calculator(name, batch_size, max_seq_len, steps, corpus_size)

# GBERT-base
name = "GBERT-base"
corpus_size = 2000000000
max_seq_len = 512
batch_size = 128
steps = 4000000
epochs = epoch_calculator(name, batch_size, max_seq_len, steps, corpus_size)

# GBERT-large
name = "GBERT-large"
corpus_size = 2000000000
max_seq_len = 512
batch_size = 2048
steps = 1000000
epochs = epoch_calculator(name, batch_size, max_seq_len, steps, corpus_size)

# GELECTRA-base
name = "GELECTRA-base"
corpus_size = 2000000000
max_seq_len = 512
batch_size = 256
steps = 766000
epochs = epoch_calculator(name, batch_size, max_seq_len, steps, corpus_size)

# GELECTRA-large
name = "GELECTRA-large"
corpus_size = 2000000000
max_seq_len = 512
batch_size = 1024
steps = 766000
epochs = epoch_calculator(name, batch_size, max_seq_len, steps, corpus_size)

# GaBERT-base
name = "GaBERT-base"
corpus_size = 159429404 # cat ga/filtered-texts/* | wc = 7937938 159429404 919788128
max_seq_len = 512
batch_size = 64
steps = 1000000
epochs = epoch_calculator(name, batch_size, max_seq_len, steps, corpus_size)

# GELECTRA-base
name = "GaELECTRA-base"
corpus_size = 159429404
max_seq_len = 512
batch_size = 256
steps = 1000000
epochs = epoch_calculator(name, batch_size, max_seq_len, steps, corpus_size)