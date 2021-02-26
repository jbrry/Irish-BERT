#!/bin/bash

# This script is to be ran on Google Cloud TPU
# Follow the steps here to set up the TPU and GCE environment first:
# 	https://cloud.google.com/tpu/docs/tutorials/roberta-pytorch


# on GCE VM
pip install --editable /usr/share/torch-xla-1.7/tpu-examples/deps/fairseq
mkdir $HOME/pytorch-tutorial-data
cd $HOME/pytorch-tutorial-data

# download necessary software
git clone https://github.com/pytorch/fairseq.git
git clone https://github.com/jbrry/Irish-BERT # need to provide login/password

mkdir data
# copy processed data
gsutil -m cp -r gs://gabert/data/gabert/pretraining_data/conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8 data/

python Irish-BERT/scripts/create_train_val_test_files.py --dataset-dir data/conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8/ga/filtered-texts/ --ratios 0.8 .1 .1 --output-dir data/roberta-data --do-shuffle

# create a sample file of 1M sentences to train SentencePiece vocab
head -n 1000000 data/roberta-data/train.txt > data/roberta-data/train_sample.txt

pip install sentencepiece

# train SPM model
# --shuffle_input_sentence=true 
python fairseq/scripts/spm_train.py --input=data/roberta-data/train_sample.txt \
	--model_prefix=data/roberta-data/sentencepiece.bpe \
	--vocab_size=30000 \
	--character_coverage=0.9999 \
	--model_type=bpe

# encode train
python fairseq/scripts/spm_encode.py --model data/roberta-data/sentencepiece.bpe.model --output_format=piece --inputs data/roberta-data/train.txt --outputs data/roberta-data/train.bpe

# encode valid
python fairseq/scripts/spm_encode.py --model data/roberta-data/sentencepiece.bpe.model --output_format=piece --inputs data/roberta-data/valid.txt --outputs data/roberta-data/valid.bpe

# encode test
python fairseq/scripts/spm_encode.py --model data/roberta-data/sentencepiece.bpe.model --output_format=piece --inputs data/roberta-data/test.txt --outputs data/roberta-data/test.bpe

# convert vocab from tab-separated to space-separated
cp data/roberta-data/sentencepiece.bpe.vocab data/roberta-data/fairseq-sentencepiece.bpe.vocab 
sed -i $'s/\t/ /g' data/roberta-data/fairseq-sentencepiece.bpe.vocab

fairseq-preprocess \
    --only-source \
    --srcdict data/roberta-data/fairseq-sentencepiece.bpe.vocab \
    --trainpref data/roberta-data/train.bpe \
    --validpref data/roberta-data/valid.bpe \
    --testpref data/roberta-data/test.bpe \
    --destdir data/roberta-data/preprocessed \
    --workers 60


export TOTAL_UPDATES=125000    # Total number of training steps
export WARMUP_UPDATES=10000    # Warmup the learning rate over this many updates
export PEAK_LR=0.0005          # Peak learning rate, adjust as needed
export TOKENS_PER_SAMPLE=512   # Max sequence length
export UPDATE_FREQ=16          # Increase the batch size 16x

export DATA_DIR=${HOME}/pytorch-tutorial-data/data/roberta-data/preprocessed

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
    --save-dir=${HOME}/checkpoints \
    --log_steps=30 \
    --max-epoch=1 \
    --skip-invalid-size-inputs-valid-test

