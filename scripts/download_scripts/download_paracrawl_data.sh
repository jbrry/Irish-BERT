#!/bin/bash

echo "Running OpusFilter to collect Opus data ..."

SRC=ga
TRG=en

# OPUS corpus name, e.g. 'paracrawl'
CORPUS=paracrawl

echo "Using corpus $CORPUS"
OUTDIR=data/ga/$CORPUS/raw

mkdir -p $OUTDIR

CONFIG=configs/opusfilter/${CORPUS}_${SRC}-${TRG}.yaml
echo "Using configuration file: $CONFIG"

opusfilter $CONFIG

cd $OUTDIR

# remove all files but the paracrawl.ga.gz
rm ParaCrawl_latest_raw_en.zip ParaCrawl_latest_xml_en-ga.xml.gz paracrawl.en.gz ParaCrawl_latest_raw_ga.zip

echo "Done"
