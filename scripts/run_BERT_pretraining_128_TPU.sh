#!/bin/bash

# Runs BERT on a TPU node
# ./scripts/run_BERT_pretraining_128_TPU.sh 5000 tpu-gabert gabert conll17_gdrive_NCI_oscar_paracrawl_filtering_None

test -z $1 && echo "Missing number of pre-training steps, e.g. '900000'"
test -z $1 && exit 1
STEPS=$1

test -z $2 && echo "Missing BERT model type: ga_bert or multilingual_bert"
test -z $2 && exit 1
BERT_MODEL=$2

test -z $3 && echo "Missing TPU Name, e.g. 'tpu-gabert'"
test -z $3 && exit 1
TPU_NAME=$3

test -z $4 && echo "Missing Bucket Name, e.g. 'gabert'"
test -z $4 && exit 1
BUCKET_NAME=$4

test -z $5 && echo "Missing model file description, e.g. list of corpora and filtering type: 'conll17_gdrive_NCI_oscar_paracrawl_filtering_None'"
test -z $5 && exit 1
FILE_DESC=$5

# original BERT paper uses 1% as the number of warmup steps
NUM_WARMUP_STEPS=` expr $STEPS / 100`

echo "Training BERT for $STEPS steps"
echo "using $NUM_WARMUP_STEPS warmup steps ..."

BERT_DIR=${HOME}/gabert/bert
DATA_DIR="gs://$BUCKET_NAME/data/gabert-v2/pretraining_data/$FILE_DESC/ga/tfrecords/seq-128"
OUTPUT_DIR="gs://$BUCKET_NAME/data/gabert-v2/model_output/${FILE_DESC}"

BERT_CONFIG=${HOME}/gabert/Irish-BERT/models/${BERT_MODEL}/bert_config.json

# if using multilingual BERT, first initialise from original checkpoint
if [ "${BERT_MODEL}" = "multilingual_bert" ]; then    
  extra_args="--init_checkpoint=${OUTPUT_DIR}/bert_model.ckpt"
else
  extra_args=""
fi

if [ $# -gt 4 ]; then
   echo "More than 4 arguments passed, assuming this is the step number to initialize from"
   INIT_STEP=$5
   extra_args="--init_checkpoint=${OUTPUT_DIR}/model.ckpt-$INIT_STEP"
 else
   extra_args=""
 fi


python3 ${BERT_DIR}/run_pretraining.py \
	--input_file=${DATA_DIR}/*.tfrecord \
	--output_dir=$OUTPUT_DIR \
	--do_train=True \
	--do_eval=False \
	--bert_config_file=${BERT_CONFIG} \
	--train_batch_size=128 \
	--max_seq_length=128 \
	--max_predictions_per_seq=20 \
	--num_train_steps=${STEPS} \
    	--save_checkpoint_steps=100000 \
	--keep_checkpoint_max=0 \
	--num_warmup_steps=${NUM_WARMUP_STEPS} \
	--learning_rate=1e-4 \
    	--use_tpu=True \
    	--tpu_name=$TPU_NAME \
	$extra_args

