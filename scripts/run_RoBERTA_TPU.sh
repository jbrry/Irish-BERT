#!/bin/bash

# This script is to be ran on Google Cloud TPU
# Instructions to set up the TPU and GCE environment: https://cloud.google.com/tpu/docs/tutorials/roberta-pytorch
# Usage:
# 	./Irish-BERT/scripts/run_RoBERTA_TPU.sh data/roberta-gabert gabert conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8

test -z $1 && echo "Missing path to directory to write output, e.g. 'data/roberta-gabert'"
test -z $1 && exit 1
ROBERTA_DATA_DIR=$1

test -z $2 && echo "Missing Bucket Name, e.g. 'gabert'"
test -z $2 && exit 1
BUCKET_NAME=$2

test -z $3 && echo "Missing model file description, e.g. list of corpora and filtering type: 'conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8'"
test -z $3 && exit 1
FILE_DESC=$3

# make sure you have downloaded Irish-BERT to:
# $HOME/gabert

# download necessary software
if [ ! -d "fairseq" ]; then
    git clone https://github.com/pytorch/fairseq.git
fi

mkdir -p data
mkdir -p $ROBERTA_DATA_DIR

# copy pretraining data from GCE bucket
if [ -d "data/filtered-texts/" ]; then
then
    echo "Output directory exists, skipping."
else
    echo "Downloading pretraining data."
    # copy pretraining data from GCE bucket
    gsutil -m cp -r gs://$BUCKET_NAME/data/gabert/pretraining_data/$FILE_DESC/ga/filtered-texts/ data
fi

if [ ! -f $ROBERTA_DATA_DIR/train.txt ]; then
	echo "Splitting input files"
	# pretraining text comes from the filtered directory
	# train, valid, and test ratios are 0.9, 0.1 and 0 (i.e. no test)
	python Irish-BERT/scripts/create_train_val_test_files.py \
		--dataset-dir data/filtered-texts/ \
		--ratios 0.9 .1 0.0 \
		--output-dir $ROBERTA_DATA_DIR \
		--random-seed 471982 \
		--do-shuffle
fi

# create a sample file of 1M sentences to train SentencePiece vocab
head -n 1000000 $ROBERTA_DATA_DIR/train.txt > $ROBERTA_DATA_DIR/train_sample.txt

pip install sentencepiece


# Learn SentencePiece model
if [ ! -f $ROBERTA_DATA_DIR/sentencepiece.bpe.model ]; then
	echo "Training SentencePiece model"
	# --shuffle_input_sentence=true 
	python fairseq/scripts/spm_train.py --input=$ROBERTA_DATA_DIR/train_sample.txt \
		--model_prefix=$ROBERTA_DATA_DIR/sentencepiece.bpe \
		--vocab_size=30000 \
		--character_coverage=0.9999 \
		--model_type=bpe
fi


# Encode as BPE
if [ ! -f $ROBERTA_DATA_DIR/train.bpe ]; then
	# encode train and valid files
	for SPLIT in train valid; do
		python fairseq/scripts/spm_encode.py --model $ROBERTA_DATA_DIR/sentencepiece.bpe.model \
			--output_format=piece \
			--inputs $ROBERTA_DATA_DIR/$SPLIT.txt \
			--outputs $ROBERTA_DATA_DIR/$SPLIT.bpe

	done
fi

# convert vocab from tab-separated to space-separated which is the format fairseq expects
cp $ROBERTA_DATA_DIR/sentencepiece.bpe.vocab $ROBERTA_DATA_DIR/fairseq-sentencepiece.bpe.vocab 
sed -i $'s/\t/ /g' $ROBERTA_DATA_DIR/fairseq-sentencepiece.bpe.vocab

fairseq-preprocess --only-source \
	--srcdict $ROBERTA_DATA_DIR/fairseq-sentencepiece.bpe.vocab \
	--trainpref $ROBERTA_DATA_DIR/train.bpe \
	--validpref $ROBERTA_DATA_DIR/valid.bpe \
	--destdir $ROBERTA_DATA_DIR/preprocessed \
	--workers 60

# Batch size is MAX_SENTENCES * UPDATE_FREQ = 16 * 16 = 256
# In https://arxiv.org/pdf/1907.11692.pdf, p.6, this is equivalent to their setting of training for 1M steps.
# TPU v3-8s have 128GB of VRAM whereas other works below use many more GPUs.
# CamemBERT: 8192 BATCH_SIZE * 100k
# UmBERTO:   2048 BATCH_SIZE * 125K

export TOTAL_UPDATES=1000000   # Total number of training steps
export WARMUP_UPDATES=100000   # Warmup the learning rate over this many updates
export PEAK_LR=0.0005	       # Peak learning rate, adjust as needed  1e-4
export TOKENS_PER_SAMPLE=512   # Max sequence length
export MAX_SENTENCES=16        # Number of sequences per batch (batch size)
export UPDATE_FREQ=16	       # Increase the batch size 16x

export DATA_DIR=${HOME}/gabert/$ROBERTA_DATA_DIR/preprocessed

python /usr/share/torch-xla-1.7/tpu-examples/deps/fairseq/train.py $DATA_DIR \
        --task masked_lm \
        --criterion masked_lm \
        --arch roberta_base \
        --sample-break-mode complete \
        --tokens-per-sample $TOKENS_PER_SAMPLE \
        --optimizer adam \
        --adam-betas '(0.9,0.98)' \
        --adam-eps 1e-6 \
        --clip-norm 0.0 \
        --lr-scheduler polynomial_decay \
        --lr $PEAK_LR \
        --warmup-updates $WARMUP_UPDATES \
        --total-num-update $TOTAL_UPDATES \
        --dropout 0.1 \
        --attention-dropout 0.1 \
        --weight-decay 0.01 \
        --update-freq $UPDATE_FREQ \
        --max-update $TOTAL_UPDATES \
        --log-format simple \
        --valid-subset=valid \
        --train-subset=train \
        --num_cores=8 \
        --metrics_debug \
        --input_shapes 16x512 18x480 21x384 \
        --save-dir=${HOME}/checkpoints/gabert/$FILE_DESC \
        --log_steps=30 \
        --max-epoch=1 \
        --skip-invalid-size-inputs-valid-test
