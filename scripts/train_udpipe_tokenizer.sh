#!/bin/bash

# keep track of where this script was run from to store the UDPipe model.
ROOTDIR=`pwd`
echo $ROOTDIR

# the tokenizer will be trained on en_ewt and ga_idt UD v2.7.
DATADIR=data/ud-treebanks
mkdir -p $DATADIR
cd $DATADIR

# this will download the latest version from GitHub.
git clone https://github.com/UniversalDependencies/UD_Irish-IDT
git clone https://github.com/UniversalDependencies/UD_English-EWT.git

OUTDIR=UD_Irish-IDT+UD_English-EWT
mkdir -p $OUTDIR

OUTFILE=$OUTDIR/train.conllu

if [[ -f "$OUTFILE" ]]; then
    echo "Removing old $OUTFILE"
    rm $OUTFILE
fi

for treebank in UD_Irish-IDT UD_English-EWT; do
    echo "Collecting data from $treebank"

    train_file=$treebank/*-ud-train.conllu
    
    if [ "$treebank" = "UD_Irish-IDT" ]; then
        for i in {1..10}; do
            cat $train_file >> $OUTFILE
        done
    else
        cat $train_file >> $OUTFILE
    fi
done

cd $ROOTDIR

UDPIPE_MODEL=udpipe_models/ga_idt+en_ewt.udpipe
COMBINED_FILE=$DATADIR/$OUTFILE

udpipe --train --tokenize $UDPIPE_MODEL $COMBINED_FILE