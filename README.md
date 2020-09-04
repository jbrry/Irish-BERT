# Irish-BERT
Repository to store helper scripts for creating an Irish BERT model.


### Raw Data
We collect raw corpora from the following sources:

---
#### CoNLL'17 Data
The CoNLL’17 raw corpus contains Wikipedia and CommonCrawl data for Irish. The files are converted from CoNLL-U format to text.

```bash
./scripts/download_conll17_data.sh
```
- location: `data/ga/conll17`

---
#### Google Drive Data
We collected corpora from various locations which are stored on Google Drive (some of these corpora are not allowed to be circulated publicly).

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
[OSCAR](https://oscar-corpus.com/) is used to download Irish CommonCrawl data. We are awaiting the un-shuffled version by the authors.
```bash
./scripts/download_oscar_data.sh
```
- location: `data/ga/oscar`

### Overview of Data 


| Corpus       | Number of Sentences |  Size (MB) |
|--------------|---------------------|------------|
| CoNLL'17     | 1,824,439           | 136        |
| Google Drive | 3,073,490           | 216        |
| ParaCrawl    | 782,769             | 137        |
| OSCAR        | 366,323             | 88         |
| Overall      | 6,046,575           | 577        |

Note: sentences are not de-duplicated or filtered. As such, they may contain duplicate sentences, large portions of `en` bitext or noisy text.

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
