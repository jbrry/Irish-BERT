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
- num sentences: `1,046,049` (TBC. whether this is line-by-line or paragraph)
---

#### OPUS Data

To download data from OPUS, the [OpusFilter](https://github.com/Helsinki-NLP/OpusFilter) tool can be used. After installing `OpusFilter` (see OpusFilter repository), the tool can be used to download data from a specific directory on OPUS, e.g. Paracrawl:

```bash
mkdir data/ga/opus/paracrawl
opusfilter configs/opusfilter/paracrawl_ga-en.yaml
```
- location: `data/ga/opus/paracrawl`
- num sentences: TBC.
---
