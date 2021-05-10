
# Analysis of SentencePiece and WordPiece Tokenizers

In the experiments below, the SentencePiece tokenizer was replaced with a WordPiece tokenizer. An initial inspection showed that the WordPiece tokenizer added many more foreign characters and emojis at the expense of Irish words/word-pieces. The noisier vocab appears to lead to lower parsing results. Note that the WordPiece-BERT model only trained for 494/500k steps due to the job timing out on Grove. The job wasn't continued in case the warmup learning rate affected convergence but this should still be a reasonably fair comparison. The same data was used, i.e. the data used for ga_BERT `v1` i.e. `conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8`.


#### Vocab Diffs
Here is a diff on the two vocabs. `-` and `+` indicates what was removed and added when using the WordPiece tokenizer. 
[sentencepiece_wordpiece_conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8_diffs.txt](https://github.com/jbrry/Irish-BERT/files/6455084/sentencepiece_wordpiece_conll17_gdrive_NCI_oscar_paracrawl_filtering_basic%2Bchar-1.0%2Blang-0.8_diffs.txt)



### Comparison of Multi-task Dependency Parser With SentencePiece and WordPiece Tokenizers

The below results compare LAS, Morph. feats accuracy, POS accuracy and XPOS accuracy predicted by a multitask model using the ga_BERT checkpoint at 500,000 pretraining steps - one with the SentencePiece and one with WordPiece:

<img src="/assets/images/ga_BERT_tokenizer_dependencies_LAS.png" style="display: block; margin: 0 auto" />

<img src="/assets/images/ga_BERT_tokenizer_feats_accuracy.png" style="display: block; margin: 0 auto" />

<img src="/assets/images/ga_BERT_tokenizer_upos_accuracy.png" style="display: block; margin: 0 auto" />

<img src="/assets/images/ga_BERT_tokenizer_xpos_accuracy.png" style="display: block; margin: 0 auto" />
