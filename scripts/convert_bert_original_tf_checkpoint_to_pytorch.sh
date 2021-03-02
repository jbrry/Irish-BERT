#!/bin/bash

test -z $1 && echo "Missing number of pre-training steps, e.g. '1000000'"
test -z $1 && exit 1
STEPS=$1

test -z $2 && echo "Missing BERT model type, e.g. 'ga_bert' or 'multilingual_bert'"
test -z $2 && exit 1
BERT_MODEL=$2

test -z $3 && echo "Missing model file description, e.g. 'NCI_filtered_None'"
test -z $3 && exit 1
FILE_DESC=$3

MODEL_DIR=models/${BERT_MODEL}
OUT_DIR=${MODEL_DIR}/output/${FILE_DESC}
PYTORCH_OUTDIR=${MODEL_DIR}/output/pytorch_models/${FILE_DESC}

mkdir -p ${OUT_DIR}
mkdir -p ${PYTORCH_OUTDIR}

# make sure to `cat vocab.txt | wc -l` to get the size of the vocabulary for the config.
BERT_CONFIG=${MODEL_DIR}/bert_config.json
WIKI_BERT_DIR="../wiki-bert-pipeline"
BERT_VOCAB=${WIKI_BERT_DIR}/data/${FILE_DESC}/ga/wordpiece/cased/vocab.txt

cp ${BERT_CONFIG} ${PYTORCH_OUTDIR}/config.json
cp ${BERT_VOCAB} ${PYTORCH_OUTDIR}

transformers-cli convert --model_type bert \
  --tf_checkpoint ${OUT_DIR}/model.ckpt-${STEPS} \
  --config ${BERT_CONFIG} \
  --pytorch_dump_output ${PYTORCH_OUTDIR}/pytorch_model.bin

# pack model as expected by AlennNLP
cd ${PYTORCH_OUTDIR}
tar -czf weights.tar.gz config.json pytorch_model.bin

