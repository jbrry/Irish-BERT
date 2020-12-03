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

The chart above shows the outputs of 5 parser runs on `ga_idt` v2.5 for each ParaCrawl corpus filter type.
The `NCI` corpus is also added in for a comparison as this is a high-quality corpus.
From the above chart, we can see that the version which uses no additional filtering has the highest score overall. That said, the highest score is achieved by one particular run and the runs with other seeds do not do as well.
The variants which use basic filtering and basic filtering with character script and language ID thresholds of 50% perform a bit worse.
The variant which ensures that all characters are in the `Latin` script (e.g. 100%) and uses a slightly higher language ID threshold of 80% does slightly better and in fact, three of the parser runs for this corpus did better than the version that uses no filtering but had an individual high-performing run.
A model trained on `NCI` with no filtering does better than all the `ParaCrawl` runs.

The main takeaway here is that no filtering does pretty well and perhaps, if using filtering, it's better to have a more strict filter.

# Corpus Sizes
<img src="/assets/images/ga_idt_paracrawl_NCI_sizes.png" style="display: block; margin: 0 auto" />

The chart above shows the number of sentences in each corpus.
As we can see, not that many sentences are removed by just applying basic filtering. Perhaps most of them have been removed by `bicleaner` already.
A small portion is removed when character-script and language ID filters are considered.
Finally, the `NCI` corpus contains far fewer sentences - around 1.7M compared to over 3M with the unfiltered `ParaCrawl` corpus.
Despite having fewer sentences, the `NCI` serves as a better corpus for training a BERT model on but `ParaCrawl` still does really well!



