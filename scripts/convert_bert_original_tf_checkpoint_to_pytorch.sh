#!/bin/bash

# number of pre-training steps
STEPS=$1

OUTDIR=output/pretraining_output_${STEPS}
PYTORCH_OUTDIR=output/pytorch_models/ga_BERT_${STEPS}

mkdir -p $OUTDIR
mkdir -p $PYTORCH_OUTDIR

BERT_CONFIG=configs/bert/bert_config.json 
cp $BERT_CONFIG $PYTORCH_OUTDIR

python -m transformers.convert_bert_original_tf_checkpoint_to_pytorch \
  --tf_checkpoint_path ${OUTDIR}/model.ckpt-${STEPS} \
  --bert_config_file ${BERT_CONFIG} \
  --pytorch_dump_path ${PYTORCH_OUTDIR}/pytorch_model.bin

# pack model as expected by AlennNLP v0.9.0

cd $PYTORCH_OUTDIR
tar -czf weights.tar.gz bert_config.json pytorch_model.bin

