# Irish-BERT
Repository to store helper scripts for creating an Irish BERT model.

### Pre-training Corpora
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

### Steps for Downloading pre-training Corpora
#### CoNLL'17 Data
```bash
./scripts/download_conll17_data.sh
```
- location: `data/ga/conll17`

---
#### Google Drive Data
```bash
# download the data
./scripts/download_gdrive_data.sh

# gather the various files into a common directory
find data/ga/gdrive/ -maxdepth 3 -type f | python scripts/gather_gdrive_data.py
```
- location: `data/ga/gdrive/gathered`

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
#### OSCAR Data
```bash
./scripts/download_oscar_data.sh
```
- location: `data/ga/oscar`

---
#### Wikipedia Data
The Wikipedia data is collected later on when running the wiki-bert-pipeline, where the above-listed data will be merged with the Wikipedia data.

### Training a BERT model with Irish data
Once you have downloaded the above data, the data can then be collected and processed so that it is ready to be fed into BERT. We use the [wiki-bert-pipeline](https://github.com/spyysalo/wiki-bert-pipeline) to tokenise, filter and create vocabularies/training files for BERT. This repository is primarily focused on using Wikipedia data. In order to use external data, see our [forked version of the wiki-bert-pipeline](https://github.com/jbrry/wiki-bert-pipeline). In particular, you will need to switch to the `external_data` branch.

```bash
git clone https://github.com/jbrry/wiki-bert-pipeline.git
cd wiki-bert-pipeline
git checkout external_data
```

You can then launch the main driver script using the `ga` language identifier:
```bash
RUN_external.sh ga
```

This will first run a python script `external_scripts/gather_external_data.py` which will collect the corpora you have downloaded using this (Irish-BERT) repository, place them into a directory along with the wikipedia articles and run the rest of the wiki-bert-pipeline mostly as normal.
