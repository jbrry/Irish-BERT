
# Analysis of ELECTRA models trained in 12 and 24 hours

In the experiment below, we train an ELECTRA-base model for 100,000 and 180,000 steps which correspond to training times of `12:48:37` and `22:57:08` respectively. 

We report multitask scores where the ELECTRA model at a specific checkpoint is used to produce the token representation.

Note that for all 100k runs, the model has very poor performance. For the 180k run, the model performs reasonably for 2/5 seeds but completely fails for 3 seeds. The paths to the saved ELECTRA models are available in the config file of each parser and it has been confirmed that all 180k parsing runs use the 180k ELECTRA checkpoint, so at this point in time, it is not known why some seeds do well and others do not.

<img src="/assets/images/gaelectra_100k_180k.png" style="display: block; margin: 0 auto" />

