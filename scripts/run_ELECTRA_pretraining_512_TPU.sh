#!/bin/bash

test -z $1 && echo "Missing model file description, copy this from wikibirt data dir, e.g. NCI_old"
test -z $1 && exit 1
FILE_DESC=$1

# location of ELECTRA repository
ELECTRA_DIR=${HOME}/gabert/electra

# location of DATA_DIR used by ELECTRA
DATA_DIR=gs://gabert/data/gabert-v2/pretraining_data/electra/${FILE_DESC}

# copy config to configure_pretraining.py
cp ${HOME}/gabert/Irish-BERT/scripts/configure_electra_pretraining_base.py ${ELECTRA_DIR}/configure_pretraining.py

# prep tfrecords (this step was done manually from inside wikibert dir for FILE_DESC)
#gsutil -m cp -r seq-512/ gs://gabert/data/gabert-v2/pretraining_data/electra/conll17_gdrive_NCI_oscar_paracrawl_wiki_filtering_document-heuristic
#gsutil cp vocab.txt gs://gabert/data/gabert-v2/pretraining_data/electra/conll17_gdrive_NCI_oscar_paracrawl_wiki_filtering_document-heuristic

# run ELECTRA
python ${ELECTRA_DIR}/run_pretraining.py --data-dir ${DATA_DIR} --model-name "electra-base-${FILE_DESC}"

