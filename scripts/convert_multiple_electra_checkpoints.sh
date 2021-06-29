#!/bin/bash

test -z $1 && echo "Missing model file description, e.g. 'conll17_gdrive_NCI_oscar_paracrawl_wiki_filtering_basic+char-1.0+lang-0.8'"
test -z $1 && exit 1
FILE_DESC=$1

test -z $2 && echo "Missing BERT model type: ga_bert, multilingual_bert or electra"
test -z $2 && exit 1
BERT_MODEL=$2

test -z $3 && echo "Missing model type, use 'generator' for MLM or 'discriminator' for classification"
test -z $3 && exit 1
MODEL_TYPE=$3

OUTDIR=models/${BERT_MODEL}/output/electra_tpu_runs/${FILE_DESC}
mkdir -p ${OUTDIR}

gsutil -m cp -r gs://gabert/data/gabert-v2/pretraining_data/electra/${FILE_DESC}/models/electra-base-${FILE_DESC}/events* ${OUTDIR}
gsutil -m cp -r gs://gabert/data/gabert-v2/pretraining_data/electra/${FILE_DESC}/models/electra-base-${FILE_DESC}/checkpoint* ${OUTDIR}
gsutil -m cp -r gs://gabert/data/gabert-v2/pretraining_data/electra/${FILE_DESC}/models/electra-base-${FILE_DESC}/graph* ${OUTDIR}

for CHKPT in 100000 200000 300000 400000 500000 600000 700000 800000 900000 1000000; do
	gsutil -m cp -r gs://gabert/data/gabert-v2/pretraining_data/electra/${FILE_DESC}/models/electra-base-${FILE_DESC}/model.ckpt-${CHKPT}* ${OUTDIR}
	
	echo "converting $CHKPT checkpoint"
	./scripts/convert_electra_original_tf_checkpoint_to_pytorch.sh ${CHKPT} ${BERT_MODEL} ${FILE_DESC} ${MODEL_TYPE}
done
