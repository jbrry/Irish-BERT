# Irish-BERT
Repository to store helper scripts for creating an Irish BERT model.

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
To download the `conll17`, `gdrive` and `oscar` datasets run the below with the appropriate corpus (or all of them).

```bash
python scripts/download_handler.py --datasets conll17 gdrive oscar
```

This will place the downloaded data in the below location:

```bash
data/ga/<corpus_name>/raw
```

Then, combine and remove non UTF-8 lines from the the files in a corpus. You can specify the argument `--bucket-size <n>` to split the corpus into files containing `n` sentences. If you want to produce just one file, specify `n` to be larger than your corpus size.

```bash
python scripts/text_processor.py --datasets conll17 gdrive oscar
```

This will place the processed data in the below location:

```bash
data/ga/<corpus_name>/processed
```

---
#### OPUS Data

To download data from OPUS, the [OpusFilter](https://github.com/Helsinki-NLP/OpusFilter) tool can be used. After installing `OpusFilter` (see OpusFilter repository), the tool can be used to download data from a specific corpus on OPUS e.g. `paracrawl` (you can add configuration files for other corpora). See `configs/opusfilter` for example configuration files.

```bash
# using 'paracrawl' corpus as an example

mkdir data/ga/opus/paracrawl
./scripts/download_opus_data.sh paracrawl
```
- location: `data/ga/opus/paracrawl`

---
#### Wikipedia Data
The Wikipedia data is collected later on when running the wiki-bert-pipeline, where the above-listed data will be merged with the Wikipedia data.

## Steps for Filtering Corpora
We use the [OpusFilter](https://github.com/Helsinki-NLP/OpusFilter) tool to filter the corpora. Please follow the instructions in the OpusFilter repository to install OpusFilter. Once you have OpusFilter installed, you need to switch to the `nlingual-rebase` branch to work with data which is not parallel text:

```bash
cd /path/to/OpusFilter
git checkout nlingual-rebase
```

Run OpusFilter on each corpus. Note: OpusFilter expects one single input file, so make sure you have run `scripts/text_processor.py` with a `--bucket-size` value larger than the number of lines in your corpus):

```bash
python scripts/filter_corpora.py --datasets conll17 gdrive oscar
```
OpusFilter also writes to the same output directory as where the input file is located. So we will break up the filtered file into chunks and place them in a `filtered` directory for each corpus:

```bash
python scripts/text_processor.py --datasets conll17 gdrive oscar --bucket-size 100000 --process-filtered --input-type processed --output-type filtered
```

## Training a BERT model with Irish data

Once you have downloaded the above data, the data can then be collected and processed so that it is ready to be fed into BERT. We use the [wiki-bert-pipeline](https://github.com/spyysalo/wiki-bert-pipeline) to tokenise, filter and create vocabularies and training files for BERT. This wiki-bert-pipeline is primarily focused on using Wikipedia data. In order to use external data, see our [forked version of the wiki-bert-pipeline](https://github.com/jbrry/wiki-bert-pipeline). In particular, you will need to switch to the `external_data` branch.

```bash
git clone https://github.com/jbrry/wiki-bert-pipeline.git
cd wiki-bert-pipeline
git checkout external_data
```

You can then launch the main driver script using the `ga` language identifier:
```bash
RUN_external.sh ga
```

This will first run a python script `external_scripts/gather_external_data.py` which will collect the corpora you have downloaded using this (Irish-BERT) repository and place them into a corpus-agonostic directory where the wikipedia articles will also be placed. The rest of the wiki-bert-pipeline will then be run mostly as normal but with the above corpora added. This will create the necessary vocabulary and `tfrecords` which BERT requires for training.

### Pre-training BERT
Once you have ran the above pipeline, the `tfrecords` should be created at:

```bash
/path/to/wiki-bert-pipeline/data/ga/tfrecords
```

You can then launch the BERT pre-training script:
```bash
# Train at seq-len of 128 for the first 90% of steps:
sbatch scripts/run_BERT_pretraining_128.job

# Train at seq-len of 512 for the last 10% of steps: (TODO)
sbatch scripts/run_BERT_pretraining_512.job

```
