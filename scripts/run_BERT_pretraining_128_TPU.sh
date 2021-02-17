#!/bin/bash

test -z $1 && echo "Missing number of pre-training steps, e.g. '900000'"
test -z $1 && exit 1
STEPS=$1

test -z $2 && echo "Missing TPU Name, e.g. 'tpu-gabert'"
test -z $2 && exit 1
TPU_NAME=$2

test -z $3 && echo "Missing Bucket Name, e.g. 'gabert'"
test -z $3 && exit 1
BUCKET_NAME=$3

test -z $4 && echo "Missing model file description, e.g. list of corpora and filtering type: 'conll17_gdrive_NCI_oscar_paracrawl_filtering_None'"
test -z $4 && exit 1
FILE_DESC=$4

# original BERT paper uses 1% as the number of warmup steps
NUM_WARMUP_STEPS=` expr $STEPS / 100`

echo "Training BERT for $STEPS steps"
echo "using $NUM_WARMUP_STEPS warmup steps ..."

BERT_DIR=path/to/bert # on TPU node.
DATA_DIR="gs://$BUCKET_NAME/data/gabert/pretraining_data/$FILE_DESC/ga/tfrecords/seq-128/"

OUTPUT_DIR="gs://$BUCKET_NAME/data/blah/blah/pretraining_output_${FILE_DESC}_${STEPS}"


#MODEL_DIR="models/${BERT_MODEL}"
#BERT_CONFIG="${MODEL_DIR}/bert_config.json"
#OUTPUT_DIR="${MODEL_DIR}/pretraining_output_${FILE_DESC}_${STEPS}"

#  --output_dir=gs://$bert_directory \
mkdir -p $OUTPUT_DIR

# if using multilingual BERT, first initialise from original checkpoint
if [ "${BERT_MODEL}" = "multilingual_bert" ]; then   
  DATA_DIR=${WIKI_BERT_DIR}/data/ga/tfrecords-multilingual_bert/seq-128
 
  ln -s $PWD/${MODEL_DIR}/bert_model.ckpt.index $PWD/${OUTPUT_DIR}/bert_model.ckpt.index
  extra_args="--init_checkpoint=${OUTPUT_DIR}/bert_model.ckpt"
else
  extra_args=""
fi

# if [ $# -gt 3 ]; then
#   echo "More than 3 arguments passed, assuming this is the step number to initialize from"
#   INIT_STEP=$4
#   extra_args="--init_checkpoint=${OUTPUT_DIR}/model.ckpt-$INIT_STEP"
# else
#   extra_args=""
# fi


python3 ${BERT_DIR}/run_pretraining.py \
	--input_file=${DATA_DIR}/*.tfrecord \
	--output_dir=$OUTPUT_DIR \
	--do_train=True \
	--do_eval=False \
	--bert_config_file=${BERT_CONFIG} \
	--train_batch_size=32 \
	--max_seq_length=128 \
	--max_predictions_per_seq=20 \
	--num_train_steps=${STEPS} \
    --save_checkpoint_steps=100000 \
	--num_warmup_steps=${NUM_WARMUP_STEPS} \
	--learning_rate=1e-4 \
    --use_tpu=True \
    --tpu_name=$tpu_name


