#!/bin/bash

#SBATCH -J 128_electra
#SBATCH --gres=gpu:rtx6000:1

# time it as 24h: #SBATCH -t 24:00:00

test -z $1 && echo "Missing number of pre-training steps"
test -z $1 && exit 1
STEPS=$1

test -z $2 && echo "Missing BERT model type: ga_bert, multilingual_bert or electra"
test -z $2 && exit 1
BERT_MODEL=$2

test -z $3 && echo "Missing model file description, copy this from wikibirt data dir, e.g. NCI_old"
test -z $3 && exit 1
FILE_DESC=$3

# original BERT paper uses 1% as the number of warmup steps
NUM_WARMUP_STEPS=` expr $STEPS / 100`

echo "Training BERT for $STEPS steps"
echo "using $NUM_WARMUP_STEPS warmup steps ..."

# wikibert is located in parent dir
parentdir="$(dirname "$PWD")"

# location of ELECTRA repository
WIKI_BERT_DIR="${parentdir}/wiki-bert-pipeline"
ELECTRA_DIR=${WIKI_BERT_DIR}/electra
INPUT_DATA_DIR=${WIKI_BERT_DIR}/data/${FILE_DESC}/ga

# copy config to configure_pretraining.py
cp scripts/configure_electra_pretraining_base_grove.py ${ELECTRA_DIR}/configure_pretraining.py

MODEL_DIR="models/${BERT_MODEL}"
#BERT_CONFIG="${MODEL_DIR}/config.json"
#OUTPUT_DIR="${MODEL_DIR}/output/${FILE_DESC}_${STEPS}"
#mkdir -p $OUTPUT_DIR

# prep data dir for ELECTRA 
# --data-dir: a directory where pre-training data, model weights, etc. are stored.
DATA_DIR=${MODEL_DIR}/${FILE_DESC}
mkdir -p ${DATA_DIR}

# prep tfrecords
ln -s "${INPUT_DATA_DIR}/electra-pretrain-tfrecords/seq-128" "${DATA_DIR}/pretrain_tfrecords"
# prep vocab
ln -s "${INPUT_DATA_DIR}/wordpiece/cased/vocab.txt" "${DATA_DIR}/vocab.txt"

# run ELECTRA
python ${ELECTRA_DIR}/run_pretraining.py --data-dir ${DATA_DIR} --model-name "electra-base-${FILE_DESC}"


# --hparams '{
#         "pretrain_tfrecords": "${DATA_DIR}/electra-pretrain-tfrecords/seq-128/*",
#         "model_dir": "${MODEL_DIR}/output/${FILE_DESC}",
#         "vocab_file": "${DATA_DIR}/wordpiece/cased/vocab.txt",
#         "vocab_size": "30101"}'