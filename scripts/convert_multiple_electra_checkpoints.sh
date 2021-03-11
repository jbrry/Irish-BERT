#!/bin/bash

for CHKPT in 50000 100000 150000 200000 250000 300000 350000; do
	echo "converting $CHKPT checkpoint"
	./scripts/convert_electra_original_tf_checkpoint_to_pytorch.sh $CHKPT conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8 discriminator
done
