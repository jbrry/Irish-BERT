#!/bin/bash

test -z $1 && echo "Missing number of pre-training steps, e.g. '1000000'"
test -z $1 && exit 1
STEPS=$1

test -z $2 && echo "Missing model file description, e.g. 'conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8'"
test -z $2 && exit 1
FILE_DESC=$2

# TF checkpoints are available on Google Drive
CHECKPOINT="/home/jbarry/ga_BERT/Irish-BERT/models/ga_bert/output/gabert-electra/$FILE_DESC/models/electra-base-irish-cased"

CONFIG="models/ga_bert/electra_base_config.json"
OUTDIR="/home/jbarry/ga_BERT/Irish-BERT/models/ga_bert/output/pytorch/gabert-electra/$FILE_DESC"

mkdir -p $OUTDIR
cp "$CONFIG" "$OUTDIR/config.json"
# vocab file should be available from the same location on Gogle drive as $CHECKPOINT
cp "$CHECKPOINT/vocab.txt" "$OUTDIR"

# use 'generator' for MLM or 'discriminator' for classification
# e.g. --discriminator_or_generator=generator to be used with ElectraForMaskedLM
MODEL_TYPE="generator"

TRANSFORMERS_DIR="$HOME/ga_BERT/transformers"

# Use the conversion script
python "$TRANSFORMERS_DIR"/src/transformers/models/electra/convert_electra_original_tf_checkpoint_to_pytorch.py \
    --tf_checkpoint_path="$CHECKPOINT/model.ckpt-$STEPS" \
    --config_file="$CONFIG" \
    --pytorch_dump_path="$OUTDIR"/pytorch_model.bin \
    --discriminator_or_generator="$MODEL_TYPE"