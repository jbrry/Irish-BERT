#!/bin/bash

# try:
# ./scripts/convert_bert_pytorch_checkpoint_to_original_tf.sh TurkuNLP/wikibert-base-ga-cased models/TurkuNLP/wikibert-base-ga-cased/ models/TurkuNLP/wikibert-base-ga-cased/pytorch_model.bin models/TurkuNLP/wikibert-base-ga-cased-tf/

test -z $1 && echo "Missing model name, e.g. 'X'"
test -z $1 && exit 1
MODEL_NAME=$1

test -z $2 && echo "Missing cache dir, e.g. 'X'"
test -z $2 && exit 1
CACHE_DIR=$2

test -z $3 && echo "Missing pytorch dir, e.g. 'X'"
test -z $3 && exit 1
PYTORCH_DIR=$3

test -z $4 && echo "Missing tf cache dir, e.g. 'X'"
test -z $4 && exit 1
TF_CACHE_DIR=$4

TRANSFORMERS_DIR="../transformers"

python ${TRANSFORMERS_DIR}/src/transformers/models/bert/convert_bert_pytorch_checkpoint_to_original_tf.py --model_name ${MODEL_NAME} \
  --cache_dir ${CACHE_DIR} \
  --pytorch_model_path ${PYTORCH_DIR} \
  --tf_cache_dir ${TF_CACHE_DIR}

