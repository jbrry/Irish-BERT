#/bin/bash

echo "Running OpusFilter to collect Opus data ..."

SRC=ga
TRG=en

# OPUS corpus name, e.g. 'paracrawl'
CORPUS=$1
echo "Using corpus $CORPUS"
mkdir -p data/ga/opus/$CORPUS

OUTDIR=data/ga/opus/$CORPUS

CONFIG=configs/opusfilter/${CORPUS}_${SRC}-${TRG}.yaml
echo "Using configuration file: $CONFIG"

opusfilter $CONFIG

echo "Done"
