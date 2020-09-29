#!/bin/bash

test -z $1 && echo "Missing number of pre-training steps"
test -z $1 && exit 1
STEPS=$1

test -z $2 && echo "Missing BERT model type: ga_bert or multilingual_bert"
test -z $2 && exit 1
BERT_MODEL=$2

MODEL_DIR=models/${BERT_MODEL}

OUT_DIR=${MODEL_DIR}/pretraining_output_${STEPS}
PYTORCH_OUTDIR=${MODEL_DIR}/pytorch_models/${BERT_MODEL}_${STEPS}

mkdir -p ${OUT_DIR}
mkdir -p ${PYTORCH_OUTDIR}

BERT_CONFIG=${MODEL_DIR}/bert_config.json  
cp $BERT_CONFIG $PYTORCH_OUTDIR

python -m transformers.convert_bert_original_tf_checkpoint_to_pytorch \
  --tf_checkpoint_path ${OUT_DIR}/model.ckpt-${STEPS} \
  --bert_config_file ${BERT_CONFIG} \
  --pytorch_dump_path ${PYTORCH_OUTDIR}/pytorch_model.bin

# pack model as expected by AlennNLP v0.9.0
cd ${PYTORCH_OUTDIR}
tar -czf weights.tar.gz bert_config.json pytorch_model.bin

