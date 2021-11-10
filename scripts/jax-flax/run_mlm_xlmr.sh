#!/bin/bash
# This script is to be ran on Google Cloud TPU
# Instructions to set up the TPU and GCE environment: https://cloud.google.com/tpu/docs/jax-quickstart-tpu-vm
#
# Usage:
#       ./run_mlm_flax.sh irish-roberta-base gabert-v2 conll17_gdrive_NCI_oscar_paracrawl_wiki_filtering_document-heuristic

test -z $1 && echo "Missing path to directory to write output, e.g. 'irish-roberta-base'"
test -z $1 && exit 1
OUTPUT_DIR=$1

test -z $2 && echo "Missing Bucket Name, e.g. 'gabert'"
test -z $2 && exit 1
BUCKET_NAME=$2

test -z $3 && echo "Missing model file description, e.g. list of corpora and filtering type: 'conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8'"
test -z $3 && exit 1
FILE_DESC=$3

mkdir -p $OUTPUT_DIR

# download necessary software
if [ ! -d "transformers" ]; then
        echo "Cloning Transformers library"
        git clone https://github.com/huggingface/transformers.git
fi

# copy pretraining data from GCE bucket
if [ -d "$OUTPUT_DIR/filtered-texts/" ]; then
        echo "Output directory exists, skipping."
else
        echo "Downloading pretraining data."
        # copy pretraining data from GCE bucket
        gsutil -m cp -r gs://$BUCKET_NAME/data/gabert/pretraining_data/$FILE_DESC/ga/filtered-texts/ $OUTPUT_DIR
fi

# create train and eval files
if [ ! -f $OUTPUT_DIR/train.txt ]; then
        echo "Splitting input files"
        # pretraining text comes from the filtered directory
        # train, valid, and test ratios are 0.9, 0.1 and 0 (i.e. no test)
        python ../create_train_val_test_files.py \
                --dataset-dir $OUTPUT_DIR/filtered-texts/ \
                --ratios 0.98 0.02 0.0 \
                --output-dir $OUTPUT_DIR
fi

export WARMUP_STEPS=10000   # Warmup the learning rate over this many updates
export TOKENS_PER_SAMPLE=128   # Max sequence length
export NUM_CORES=8

#LM_PATH="./transformers/examples/flax/language-modeling"
TRAIN_PATH="$OUTPUT_DIR/train.txt"
VALIDATION_PATH="$OUTPUT_DIR/valid.txt"

# NOTE: requires symbolic link to 'xla_spawn.py' and 'run_mlm.py' from transformers/examples/pytorch/

echo "Running training"
python xla_spawn.py --num_cores "$NUM_CORES" run_mlm.py \
    --output_dir="$OUTPUT_DIR" \
    --model_name_or_path="xlm-roberta-base" \
    --train_file="$TRAIN_PATH" \
    --validation_file="$VALIDATION_PATH" \
    --do_train --do_eval \
    --preprocessing_num_workers 64 \
    --max_seq_length="$TOKENS_PER_SAMPLE" \
    --weight_decay="0.01" \
    --per_device_train_batch_size="32" \
    --per_device_eval_batch_size="32" \
    --overwrite_output_dir \
    --warmup_steps="$WARMUP_STEPS" \
    --num_train_epochs=40 \
    --learning_rate=1e-4 \
    --adam_beta1="0.9" \
    --adam_beta2="0.98" \
    --logging_steps="5000" \
    --save_steps="5000" \
    --eval_steps="5000" \
    --line_by_line

