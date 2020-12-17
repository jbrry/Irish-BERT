#!/bin/bash

# Usage:
#       ./scripts/convert_bert_original_tf_checkpoint_to_pytorch_finetuned.sh 50000 ga_bert NCI_filtered_none 200000 twitter_filtering_None

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

MODEL_DIR=models/${BERT_MODEL}
OUT_DIR=${MODEL_DIR}/pretraining_output_${TRAINED_FILE_DESC}_${INIT_STEP}_${FINETUNE_CORPUS_DESC}_${FINETUNE_STEPS}
PYTORCH_OUTDIR=${MODEL_DIR}/pytorch_models/pretraining_output_${TRAINED_FILE_DESC}_${INIT_STEP}_${FINETUNE_CORPUS_DESC}_${FINETUNE_STEPS}

mkdir -p ${OUT_DIR}
mkdir -p ${PYTORCH_OUTDIR}

if [ -s "${OUT_DIR}" ]; then
    echo "Found output directory: ${OUT_DIR}" >&2
else
    echo "Could not find output directory: ${OUT_DIR}" >&2
    exit 1
fi

echo "Writing converted model to ${PYTORCH_OUTDIR}"

# make sure to `cat vocab.txt | wc -l` to get the size of the vocabulary for the config.
BERT_CONFIG=${MODEL_DIR}/bert_config.json
WIKI_BERT_DIR="../wiki-bert-pipeline"
BERT_VOCAB=${WIKI_BERT_DIR}/data/${TRAINED_FILE_DESC}/ga/wordpiece/cased/vocab.txt
cp ${BERT_CONFIG} ${PYTORCH_OUTDIR}
# make a 'config.json' which is expected by Hugging Face
cp ${BERT_CONFIG} ${PYTORCH_OUTDIR}/config.json
cp ${BERT_VOCAB} ${PYTORCH_OUTDIR}


python -m transformers.convert_bert_original_tf_checkpoint_to_pytorch \
  --tf_checkpoint_path ${OUT_DIR}/model.ckpt-${FINETUNE_STEPS} \
  --bert_config_file ${BERT_CONFIG} \
  --pytorch_dump_path ${PYTORCH_OUTDIR}/pytorch_model.bin


# pack model as expected by AlennNLP v0.9.0
cd ${PYTORCH_OUTDIR}
tar -czf weights.tar.gz bert_config.json pytorch_model.bin

echo "Done"