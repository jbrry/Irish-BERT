# Irish-BERT
Repository to store helper scripts for creating an Irish BERT model.

## Pretrained models
The pretrained models are available to download from https://huggingface.co/models
*   **[`gaBERT v1`](https://huggingface.co/DCU-NLP/bert-base-irish-cased-v1)**: Uses BERT-Base architecture.

```
from transformers import AutoModelWithLMHead, AutoTokenizer
import torch

tokenizer = AutoTokenizer.from_pretrained("DCU-NLP/bert-base-irish-cased-v1")
model = AutoModelWithLMHead.from_pretrained("DCU-NLP/bert-base-irish-cased-v1")

sequence = f"Ceoltóir {tokenizer.mask_token} ab ea Johnny Cash."

input = tokenizer.encode(sequence, return_tensors="pt")
mask_token_index = torch.where(input == tokenizer.mask_token_id)[1]

token_logits = model(input)[0]
mask_token_logits = token_logits[0, mask_token_index, :]

top_5_tokens = torch.topk(mask_token_logits, 5, dim=1).indices[0].tolist()

for token in top_5_tokens:
    print(sequence.replace(tokenizer.mask_token, tokenizer.decode([token])))
```

## Set up
[Conda](https://conda.io/) can be used to set up a virtual environment to use the software.

1.  [Download and install Conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html).

2.  Create a Conda environment with Python 3.7:

    ```
    conda create -n ga_BERT python=3.7
    ```
    
3.  Activate the Conda environment:

    ```
    conda activate ga_BERT
    ```

4. Prepare working directory:
The repository will follow the below layout, first create a root directory which will store this repository as well as the other repositories we will use:
```bash
mkdir ga_BERT
cd ga_BERT
```

Then install this repository:

```bash
git clone https://github.com/jbrry/Irish-BERT.git

# install wiki-bert-pipeline
git clone https://github.com/jbrry/wiki-bert-pipeline

# optionally install OpusFilter (see below)
git clone https://github.com/Helsinki-NLP/OpusFilter.git
```

This should produce the below directory structure. In general, we will download all external repositories in the root directory `ga_BERT`.

```
ga_BERT
└───Irish-BERT
└───wiki-bert-pipeline
└───OpusFilter 
```

We use our forked version of the [wiki-bert-pipeline](https://github.com/jbrry/wiki-bert-pipeline) to create our vocabulary and pre-training data for BERT/ELECTRA. Please follow the instructions to set up the `wiki-bert-pipeline` in its README. If you want to include [OpusFilter](https://github.com/Helsinki-NLP/OpusFilter) filtering, please install `OpusFilter` following the instructions in its README. Note that the `VariKN` and `eflomal` dependencies are not required for our purposes. To run `OpusFilter` on non-parallel data, switch to the `nlingual-rebase` branch in the `OpusFilter` repository. 

There are some other pieces of software you will need to download. We use [rclone](https://rclone.org/) to download files from Google Drive. You will need to download and configure `rclone` to download the `oscar` corpus as well as the files we have collated on Google Drive (bear in mind, these scripts won't work for you if you do not have access to our shared folder on Google Drive). For external researchers outside of this project, these scripts may not be of much relevance to you but they can be modified to work with your own data.

## Pre-training Corpora
We collect raw corpora for pre-training from the following sources:
- The Irish portion of [CoNLL 2017 Shared Task - Automatically Annotated Raw Texts and Word Embeddings](https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-1989) (CoNLL'17)
- Scraped Irish data from previous NLP projects and licensed corpora which are stored on Google Drive (Google Drive)
- Irish data collected from [OPUS](http://opus.nlpl.eu/), e.g. ParaCrawl
- The un-shuffled version of the Irish data from [OSCAR](https://oscar-corpus.com/) which filters [Common Crawl](https://commoncrawl.org/) data
- The `ga` portion of Wikipedia. To extract the `ga` texts we use the [wiki-bert-pipeline](https://github.com/spyysalo/wiki-bert-pipeline)

### Overview of Data 

| Corpus       | Number of Sentences |  Size (MB) |
|--------------|---------------------|------------|
| CoNLL'17     | 1,824,439           | 136        |
| Google Drive | 3,073,490           | 216        |
| ParaCrawl    | 782,769             | 137        |
| OSCAR        | 366,323             | 88         |
| Wikipedia    | 443,277             | 34         |
| Overall      | 6,489,852           | 611        |

NOTE: the above sentences are not de-duplicated or filtered. As such, they may contain duplicate sentences, large portions of `en` bitext or noisy text.

## Steps for Downloading pre-training Corpora
To download the `conll17`, `gdrive`, `NCI` `oscar` and `paracrawl` datasets run the below with the appropriate corpus (or all of them).

```bash
python scripts/download_handler.py --datasets conll17 gdrive NCI oscar paracrawl
```

This will place the downloaded data in the below location:

```bash
data/ga/<corpus_name>/raw
```

Then, combine and remove non UTF-8 lines from the the files in a corpus. You can specify the argument `--bucket-size <n>` to split the corpus into files containing `n` sentences. If you want to produce just one file, specify `n` to be larger than your corpus size.

```bash
python scripts/text_processor.py --datasets conll17 gdrive NCI oscar paracrawl --bucket-size 100000 --input-type raw --output-type processed
```

This will place the processed data in the below location:

```bash
data/ga/<corpus_name>/processed
```

---
#### Wikipedia Data
The Wikipedia data is collected later on when running the `wiki-bert-pipeline`, where the above-listed data will be merged with the Wikipedia data.

## Training a BERT model with Irish data

To prepare the data for BERT pretraining, you will need to install our fork of the `wiki-bert-pipeline`. In particular, you will need to switch to the `external_data` branch.

```bash
# if you haven't already cloned wiki-bert-pipeline
cd to parent directory of this folder, e.g. 'ga_BERT'
git clone https://github.com/jbrry/wiki-bert-pipeline.git
cd wiki-bert-pipeline
git checkout external_data
```

You can then collect the relevant corpora and launch the main driver script as well as specify the type of filtering to be applied. For more information, see the available arguments in [external_scripts/gather_external_data.py](https://github.com/jbrry/wiki-bert-pipeline/blob/external_data/external_scripts/gather_external_data.py) 

```
python external_scripts/gather_external_data.py --datasets NCI --input-type processed --filter-type basic+char-@+lang-@ --char-filter-threshold 1.0 --lang-filter-threshold 0.8 --no-wiki
```

This will first run a python script `external_scripts/gather_external_data.py` which will collect the corpora you have downloaded using this (Irish-BERT) repository and place them into a corpus-agonostic directory where the wikipedia articles will also be placed (`--no-wiki` will skip downloading the Wikipedia files). The rest of the wiki-bert-pipeline will then be run mostly as normal but with the above corpora added. This will create the necessary vocabulary and `tfrecords` which BERT requires for training.

### Pre-training BERT
Once you have ran the above pipeline, the `tfrecords` should be created at:

```bash
/path/to/wiki-bert-pipeline/data/<run_name>/ga/tfrecords
```

You can then launch the BERT pre-training script:
```bash
# Train at seq-len of 128 for the first 90% of steps:
sbatch scripts/run_BERT_pretraining_128.job

# Train at seq-len of 512 for the last 10% of steps: (you will need to write this file yourself, as we did not train at sequence length of 512 with GPU)
# See: scripts/run_BERT_pretraining_512_TPU.sh for appropriate parameter values
sbatch scripts/run_BERT_pretraining_512.job
```
If you have access to a TPU, the following files can be run for BERT pretraining:
```bash
# Train at seq-len of 128 for the first 90% of steps:
sbatch scripts/run_BERT_pretraining_128_TPU.sh

# Train at seq-len of 512 for the last 10% of steps:
sbatch scripts/run_BERT_pretraining_512_TPU.sh
```

### Pre-training ELECTRA
We also train [ELECTRA](https://github.com/google-research/electra) models. For this, we use the same pretraining data and `vocab.txt` produced by `wiki-bert-pipeline`. We will create our own `TFRecords` specific to ELECTRA pretraining:

```bash
./scripts/build_pretraining_dataset_ELECTRA.sh
```
Once the pretraining data is prepared for ELECTRA, change directory to your clone of ELECTRA. The pretraining configuration we used can be found at `scripts/configure_electra_pretraining_base.py`. Specifically, we overwrote the parameters in [configure_pretraining](https://github.com/google-research/electra/blob/master/configure_pretraining.py) to use our parameters.

To train the ELECTRA model on a TPU with Google Cloud Storage, run (where <file_description> is the string used in the `wiki-bert-pipeline` at `wiki-bert-pipeline/data/<file_description>`:

```
python3 run_pretraining.py --data-dir gs://gabert-electra/pretraining_data/electra/<file_description> \
    --model-name electra-base-irish-cased

```
Training takes about 12 hours for every 50,000 steps.

### Using/ Inspecting Language Models

To use the models or visualise the masked-fill capabilities, you will first need to download the model checkpoints. You will then need to use the `transformers` library to convert the TensorFlow checkpoints to PyTorch. You may need to adjust some of the paths if they are different on your filesystem.

```
# Convert BERT checkpoint
scripts/convert_bert_original_tf_checkpoint_to_pytorch.sh <step_size> <bert_model> <file_desc>

# Convert ELECTRA checkpoint
scripts/convert_electra_original_tf_checkpoint_to_pytorch.sh <step_size> <file_desc> <model_type>

```

To use the models with `transformers`, just provide the full path to your local copy of these models, where the directory should contain the model config file: `config.json`, the vocabulary: `vocab.txt` and the PyTorch weights `pytorch_model.bin`. Once you have these files locally, you can run the below to inspect the masked-fill capabilities of the model:

```
python scripts/inspect_lm_huggingface.py
```
