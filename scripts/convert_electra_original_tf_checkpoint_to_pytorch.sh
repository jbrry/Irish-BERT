#!/bin/bash

CHECKPOINT="models/ga_bert/output/electra_base/"
CONFIG="models/ga_bert/output/electra_base/config.json"
OUTDIR="models/ga_bert/output/pytorch/electra_base/"

mkdir -p $OUTDIR
cp $CONFIG $OUTDIR

# use 'generator' for MLM or 'discriminator' for classification
# e.g. --discriminator_or_generator=generator to be used with ElectraForMaskedLM
MODEL_TYPE="generator"

TRANSFORMERS_DIR="$HOME/ga_BERT/transformers"

# Use the conversion script
python "$TRANSFORMERS_DIR"/src/transformers/models/electra/convert_electra_original_tf_checkpoint_to_pytorch.py \
    --tf_checkpoint_path="$CHECKPOINT" \
    --config_file="$CONFIG" \
    --pytorch_dump_path="$OUTDIR"/pytorch_model.bin \
    --discriminator_or_generator="$MODEL_TYPE"