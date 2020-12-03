We use [ParaCrawl](https://paracrawl.eu/) version `7.1` to create a BERT model from scratch in Irish.
We consider four variants of filtering on the raw ParaCrawl data (where we use the [OpusFilter](https://github.com/Helsinki-NLP/OpusFilter/tree/master/opusfilter) package for filtering):

1. No filtering (raw data is used as is)
2. Basic filtering (sentences over 512 tokens are removed, HTML, sentences which are over 60% punctuation or are over 60% digit characters)
3. Basic filtering and `Latin` script filtering with a threshold of 50% and language ID filters of 50%.
4. Basic filtering and `Latin` script filtering with a threshold of 100% and language ID filters of 80%.


We train a BERT model with its own vocabulary using the [wiki-bert-pipeline]().
See the `external_data` branch to be able to collect external data and place it into the pipeline.
The scripts have been modified to work with `opusfilter` as well.

# Results
<img src="/assets/images/ga_idt_paracrawl_NCI.png" style="display: block; margin: 0 auto" />


# Corpus Sizes
<img src="/assets/images/ga_idt_paracrawl_NCI_sizes.png" style="display: block; margin: 0 auto" />





