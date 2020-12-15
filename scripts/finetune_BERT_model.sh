#!/bin/bash

#SBATCH -J 128_bert
#SBATCH --gres=gpu:rtx6000:1

# this script assumes you have already trained a bert model and you want finetune it on some other corpus.
# usage: sbatch scripts/finetune_BERT_model.sh 50000 ga_bert NCI_filtered_none 200000 twitter_filtering_None

test -z $1 && echo "Missing number of fine-tuning steps"
test -z $1 && exit 1
FINETUNE_STEPS=$1

test -z $2 && echo "Missing BERT model type: ga_bert or multilingual_bert"
test -z $2 && exit 1
BERT_MODEL=$2

test -z $3 && echo "Missing trained model file description"
test -z $3 && exit 1
TRAINED_FILE_DESC=$3

test -z $4 && echo "Missing initialisation step number from pretrained model"
test -z $4 && exit 1
INIT_STEP=$4

test -z $5 && echo "Missing finetuning corpus description, e.g. paracrawl_filtering_None"
test -z $5 && exit 1
FINETUNE_CORPUS_DESC=$5

# original BERT paper uses 1% as the number of warmup steps
NUM_WARMUP_STEPS=` expr $FINETUNE_STEPS / 100`

echo "Finetuning BERT for $FINETUNE_STEPS steps"
echo "using $NUM_WARMUP_STEPS warmup steps ..."

# location of BERT repository
WIKI_BERT_DIR="../wiki-bert-pipeline"
BERT_DIR=${WIKI_BERT_DIR}/bert
DATA_DIR=${WIKI_BERT_DIR}/data/${FINETUNE_CORPUS_DESC}/ga/tfrecords/seq-128

MODEL_DIR="models/${BERT_MODEL}"
BERT_CONFIG="${MODEL_DIR}/bert_config.json"
OUTPUT_DIR="${MODEL_DIR}/pretraining_output_${TRAINED_FILE_DESC}_${INIT_STEP}_${FINETUNE_CORPUS_DESC}_${FINETUNE_STEPS}"
mkdir -p $OUTPUT_DIR


python ${BERT_DIR}/run_pretraining.py \
	--input_file=${DATA_DIR}/* \
	--output_dir=$OUTPUT_DIR \
	--do_train=True \
	--do_eval=False \
	--bert_config_file=${BERT_CONFIG} \
	--train_batch_size=32 \
	--max_seq_length=128 \
	--max_predictions_per_seq=20 \
	--num_train_steps=${FINETUNE_STEPS} \
	--num_warmup_steps=${NUM_WARMUP_STEPS} \
	--learning_rate=1e-4

