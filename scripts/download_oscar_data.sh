#!/bin/bash

# using de-duplicated source / only shuffled versions are available publicly
IRISH_OSCAR_DEDUP="https://oscar-public.huma-num.fr/shuffled/ga_dedup.txt.gz"
OUTDIR=data/ga/oscar

mkdir -p $OUTDIR
cd $OUTDIR
wget $IRISH_OSCAR_DEDUP
gunzip ga_dedup.txt.gz

echo "done"
