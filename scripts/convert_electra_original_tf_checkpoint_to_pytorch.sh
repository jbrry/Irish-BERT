#!/bin/bash

test -z $1 && echo "Missing number of pre-training steps, e.g. '1000000'"
test -z $1 && exit 1
STEPS=$1

test -z $2 && echo "Missing model file description, e.g. 'conll17_gdrive_NCI_oscar_paracrawl_wiki_filtering_basic+char-1.0+lang-0.8'"
test -z $2 && exit 1
FILE_DESC=$2

test -z $3 && echo "Missing model type, use 'generator' for MLM or 'discriminator' for classification"
test -z $3 && exit 1
MODEL_TYPE=$3

# You may need to change this path according to how you set up this directory.
GABERT_DIR="/home/${USER}/spinning-storage/${USER}/ga_BERT"

CHECKPOINT="$GABERT_DIR/Irish-BERT/models/electra/${FILE_DESC}/models/electra-base-${FILE_DESC}"
CONFIG="$GABERT_DIR/Irish-BERT/models/electra/electra_base_${MODEL_TYPE}_config.json"
OUTDIR="$GABERT_DIR/Irish-BERT/models/electra/output/pytorch/$FILE_DESC/electra-base-${FILE_DESC}-${MODEL_TYPE}-${STEPS}"

# TF checkpoints are available on Google Drive
#CHECKPOINT="$GABERT_DIR/Irish-BERT/models/ga_bert/output/electra/$FILE_DESC/models/electra-base-irish-cased"

mkdir -p $OUTDIR
cp "$CONFIG" "$OUTDIR/config.json"
cp "$GABERT_DIR/Irish-BERT/models/electra/$FILE_DESC/vocab.txt" "$OUTDIR"

TRANSFORMERS_DIR="$GABERT_DIR/transformers"

# Use the conversion script
python "$TRANSFORMERS_DIR"/src/transformers/models/electra/convert_electra_original_tf_checkpoint_to_pytorch.py \
    --tf_checkpoint_path="$CHECKPOINT/model.ckpt-$STEPS" \
    --config_file="$CONFIG" \
    --pytorch_dump_path="$OUTDIR"/pytorch_model.bin \
    --discriminator_or_generator="$MODEL_TYPE"

# pack model as expected by AlennNLP
cd "$OUTDIR"
tar -czf weights.tar.gz config.json pytorch_model.bin