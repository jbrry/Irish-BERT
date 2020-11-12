#!/bin/bash

test -z $1 && echo "Missing number of pre-training steps"
test -z $1 && exit 1
STEPS=$1

test -z $2 && echo "Missing BERT model type: ga_bert or multilingual_bert"
test -z $2 && exit 1
BERT_MODEL=$2

test -z $3 && echo "Missing model file description, 'NCI_filtered_none'"
test -z $3 && exit 1
FILE_DESC=$3

MODEL_DIR=models/${BERT_MODEL}
OUT_DIR=${MODEL_DIR}/pretraining_output_${STEPS}-${FILE_DESC}
PYTORCH_OUTDIR=${MODEL_DIR}/pytorch_models/pretraining_output_${STEPS}-${FILE_DESC}

mkdir -p ${OUT_DIR}
mkdir -p ${PYTORCH_OUTDIR}

# make sure to `cat vocab.txt | wc -l` to get the size of the vocabulary for the config.
BERT_CONFIG=${MODEL_DIR}/bert_config.json
WIKI_BERT_DIR="../wiki-bert-pipeline"
BERT_VOCAB=${WIKI_BERT_DIR}/data/${FILE_DESC}/ga/wordpiece/cased/vocab.txt
cp ${BERT_CONFIG} ${PYTORCH_OUTDIR}
cp ${BERT_VOCAB} ${PYTORCH_OUTDIR}

python -m transformers.convert_bert_original_tf_checkpoint_to_pytorch \
  --tf_checkpoint_path ${OUT_DIR}/model.ckpt-${STEPS} \
  --bert_config_file ${BERT_CONFIG} \
  --pytorch_dump_path ${PYTORCH_OUTDIR}/pytorch_model.bin

# pack model as expected by AlennNLP v0.9.0
cd ${PYTORCH_OUTDIR}
tar -czf weights.tar.gz bert_config.json pytorch_model.bin

