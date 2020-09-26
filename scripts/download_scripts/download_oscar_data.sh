#!/bin/bash

IRISH_OSCAR_UNSHUFFLED="" # you need to contact OSCAR maintainers for un-shuffled version
OUTDIR=data/ga/oscar/raw

mkdir -p $OUTDIR
cd $OUTDIR

wget $IRISH_OSCAR_UNSHUFFLED

echo "done"
