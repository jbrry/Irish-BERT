#!/bin/bash

LM_PATH="/home/jbarry/ga_BERT/transformers/examples/flax/language-modeling"
TRAIN_PATH="/home/jbarry/ga_BERT/Irish-BERT/data/ga/oscar/train.txt"

python "$LM_PATH/run_mlm_flax.py" \
    --output_dir="./irish-roberta-base" \
    --model_type="roberta" \
    --config_name="./irish-roberta-base" \
    --tokenizer_name="./irish-roberta-base" \
    --train_file="$TRAIN_PATH" \
    --do_train --do_eval \
    --max_seq_length="128" \
    --weight_decay="0.01" \
    --per_device_train_batch_size="16" \
    --per_device_eval_batch_size="16" \
    --overwrite_output_dir \
    --warmup_steps="1000" \
    --overwrite_output_dir \
    --num_train_epochs="18" \
    --adam_beta1="0.9" \
    --adam_beta2="0.98" \
    --logging_steps="500" \
    --save_steps="100" \
    --eval_steps="100"
    
