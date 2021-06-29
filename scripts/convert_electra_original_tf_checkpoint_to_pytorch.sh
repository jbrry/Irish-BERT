#!/bin/bash

# /scripts/convert_electra_original_tf_checkpoint_to_pytorch.sh ${CHKPT} ${BERT_MODEL} ${FILE_DESC} ${MODEL_TYPE}

test -z $1 && echo "Missing number of pre-training steps, e.g. '1000000'"
test -z $1 && exit 1
STEPS=$1

test -z $2 && echo "Missing BERT model type: ga_bert, multilingual_bert or electra"
test -z $2 && exit 1
BERT_MODEL=$2

test -z $3 && echo "Missing model file description, e.g. 'conll17_gdrive_NCI_oscar_paracrawl_wiki_filtering_basic+char-1.0+lang-0.8'"
test -z $3 && exit 1
FILE_DESC=$3

test -z $4 && echo "Missing model type, use 'generator' for MLM or 'discriminator' for classification"
test -z $4 && exit 1
MODEL_TYPE=$4

# You may need to change this path according to how you set up this directory.
GABERT_DIR="/home/${USER}/spinning-storage/${USER}/ga_BERT"

MODEL_DIR=models/${BERT_MODEL}
OUTDIR=${MODEL_DIR}/output/electra_tpu_runs/${FILE_DESC}

PYTORCH_OUTDIR=${MODEL_DIR}/output/electra_tpu_runs/pytorch_models/electra-base-${FILE_DESC}-${MODEL_TYPE}-${STEPS}
mkdir -p $PYTORCH_OUTDIR

CONFIG="$GABERT_DIR/Irish-BERT/models/${BERT_MODEL}/electra_base_${MODEL_TYPE}_config.json"
cp "$CONFIG" "$PYTORCH_OUTDIR/config.json"

WIKI_BERT_DIR="../wiki-bert-pipeline"
BERT_VOCAB=${WIKI_BERT_DIR}/data/${FILE_DESC}/ga/wordpiece/cased/vocab.txt

cp ${BERT_VOCAB} ${PYTORCH_OUTDIR}

TRANSFORMERS_DIR="$GABERT_DIR/transformers"

# Use the conversion script
python "$TRANSFORMERS_DIR"/src/transformers/models/electra/convert_electra_original_tf_checkpoint_to_pytorch.py \
    --tf_checkpoint_path="$OUTDIR/model.ckpt-$STEPS" \
    --config_file="$CONFIG" \
    --pytorch_dump_path="$PYTORCH_OUTDIR"/pytorch_model.bin \
    --discriminator_or_generator="$MODEL_TYPE"

# pack model as expected by AlennNLP
cd "$PYTORCH_OUTDIR"
tar -czf weights.tar.gz config.json pytorch_model.bin