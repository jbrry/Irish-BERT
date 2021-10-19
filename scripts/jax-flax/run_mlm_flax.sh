#!/bin/bash

python transformers/examples/flax/language-modeling/run_mlm_flax.py \
    --output_dir="./irish-roberta-base" \
    --model_type="roberta" \
    --config_name="./irish-roberta-base" \
    --tokenizer_name="./irish-roberta-base" \
    --dataset_name="oscar" \
    --dataset_config_name="unshuffled_deduplicated_ga" \
    --max_seq_length="128" \
    --weight_decay="0.01" \
    --per_device_train_batch_size="128" \
    --per_device_eval_batch_size="128" \
    --overwrite_output_dir \
    --warmup_steps="1000" \
    --overwrite_output_dir \
    --num_train_epochs="18" \
    --adam_beta1="0.9" \
    --adam_beta2="0.98" \
    --logging_steps="500" \
    --save_steps="2500" \
    --eval_steps="2500" \
    --push_to_hub 
    
