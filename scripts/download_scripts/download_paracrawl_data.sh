#/bin/bash

echo "Running OpusFilter to collect Opus data ..."

SRC=ga
TRG=en

# OPUS corpus name, e.g. 'paracrawl'
CORPUS=paracrawl
echo "Using corpus $CORPUS"
mkdir -p data/ga/$CORPUS

OUTDIR=data/ga/$CORPUS

CONFIG=configs/opusfilter/${CORPUS}_${SRC}-${TRG}.yaml
echo "Using configuration file: $CONFIG"

opusfilter $CONFIG

echo "Done"
