#!/bin/bash

# Example usage:
#   ./scripts/build_pretraining_dataset_ELECTRA.sh conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8 gabert

test -z $1 && echo "Missing model file description, e.g. list of corpora and filtering type: 'conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8'"
test -z $1 && exit 1
FILE_DESC=$1

test -z $2 && echo "Missing Bucket Name, e.g. 'gabert'"
test -z $2 && exit 1
BUCKET_NAME=$2

# Store electra repository in parent directory of this folder
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )";
TARGET_DIRECTORY="${DIR%/*/*}"

echo "Downloading electra to... $TARGET_DIRECTORY"

# download necessary software
if [ ! -d "$TARGET_DIRECTORY/electra" ]; then
	git clone https://github.com/google-research/electra.git
fi

cd $TARGET_DIRECTORY/electra

DATA_DIR="../wiki-bert-pipeline/data/$FILE_DESC/ga/"
CORPUS_DIR="$DATA_DIR/filtered-texts"
VOCAB_FILE="$DATA_DIR/wordpiece/cased/vocab.txt"

MAX_SEQ_LEN=512
OUTPUT_DIR="../electra-pretraining-${MAX_SEQ_LEN}"
mkdir -p $OUTPUT_DIR

echo "Building pretraining dataset..."

python build_pretraining_dataset.py --corpus-dir $CORPUS_DIR \
    --vocab-file $VOCAB_FILE \
    --output-dir $OUTPUT_DIR --max-seq-length $MAX_SEQ_LEN \
    --num-processes 50 --no-lower-case

echo "Uploading pretraining data to GCE bucket..."
gsutil -m cp -r $OUTPUT_DIR gs://$BUCKET_NAME/data/gabert/pretraining_data/electra/$FILE_DESC/pretrain_tfrecords
gsutil cp $VOCAB_FILE gs://$BUCKET_NAME/data/gabert/pretraining_data/electra/$FILE_DESC/