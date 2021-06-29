#!/bin/bash

test -z $1 && echo "Missing model file description, e.g. 'conll17_gdrive_NCI_oscar_paracrawl_wiki_filtering_basic+char-1.0+lang-0.8'"
test -z $1 && exit 1
FILE_DESC=$1

test -z $2 && echo "Missing BERT model type: ga_bert or multilingual_bert"
test -z $2 && exit 1
BERT_MODEL=$2

OUTDIR=models/${BERT_MODEL}/output/bert_tpu_runs/${FILE_DESC}
mkdir -p ${OUTDIR}

gsutil -m cp -r gs://gabert/data/gabert-v2/model_output/${FILE_DESC}/events* ${OUTDIR}
gsutil -m cp -r gs://gabert/data/gabert-v2/model_output/${FILE_DESC}/checkpoint* ${OUTDIR}
gsutil -m cp -r gs://gabert/data/gabert-v2/model_output/${FILE_DESC}/graph* ${OUTDIR}

for CHKPT in 0 100000 200000 300000 400000 450000 500000 550000 575000 600000; do
	gsutil -m cp -r gs://gabert/data/gabert-v2/model_output/${FILE_DESC}/model.ckpt-${CHKPT}* ${OUTDIR}
	
	echo "converting $CHKPT checkpoint"
	./scripts/convert_bert_original_tf_checkpoint_to_pytorch.sh $CHKPT ${BERT_MODEL} ${FILE_DESC}
done
