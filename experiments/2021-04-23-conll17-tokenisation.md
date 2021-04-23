
# Analysis of Conll17 Tokenisation Bug

The segmenter in wiki-bert-pipeline operates on [a line-by-line basis](https://github.com/jbrry/wiki-bert-pipeline/blob/bfe374cde2f0b4a7d517514b1ab5d4bd2c86e9c6/scripts/udtokenize.py#L62) which means that if the inputs are paragraphs of text spanning over multiple lines, the script will split at the end of the line even if it is not where the tokeniser predicts the final token to be.

To analyse the effect of this tokenisation bug, a backup copy of the data directory was made: `conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8-conll17-tokenization-bug-backup` and in the original `conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8`, only the `conll17`-related files were replaced.

```
# bugged

(base) jbarry@g001:~/spinning-storage/jbarry/ga_BERT/wiki-bert-pipeline/data/conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8-conll17-tokenization-bug-backup/ga/filtered-texts$ head conll17_00

Iarscoláire é de chuid na meánscoile Coláiste Eoin .
Tosaíonn sí taobh thoir
thuaidh de Leithinis Rinn York in oirthuaisceart na hAstráile agus síneann sí
2,000 ciliméadar ó dheas le cósta Queensland .
Foirm a díorthaíodh ar dtús ó
fhoirgnimh Chríostaí nó phágánacha , oiriúnaithe don reiligiún .
chónaithe an tomhaltóra , nó i dtír pháirtí na cosanta , má thograíonn an
tomhaltóir sin , a thabharfar breithiúnas sa chás .
ghabáil do na glantsluagaib arna Nach rachainn 'un cainte léi .
Throid teaghlach na Hapsburg ( na hImpirí Ferdinand II agus III agus Pilib IV na

```


In the original repository, all `conll17` related files were removed and the pipeline was run again (with the conll17 tokenisation bug fixed). Notice how the tokenisation is now fixed below:

```
# bug fix

(opusfilter) jbarry@g102:~/spinning-storage/jbarry/ga_BERT/wiki-bert-pipeline/data/conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8/ga/filtered-texts$ head conll17_00
Iarscoláire é de chuid na meánscoile Coláiste Eoin .
Tosaíonn sí taobh thoir thuaidh de Leithinis Rinn York in oirthuaisceart na hAstráile agus síneann sí 2,000 ciliméadar ó dheas le cósta Queensland .
Foirm a díorthaíodh ar dtús ó fhoirgnimh Chríostaí nó phágánacha , oiriúnaithe don reiligiún .
Is i dtír chónaithe an tomhaltóra , nó i dtír pháirtí na cosanta , má thograíonn an tomhaltóir sin , a thabharfar breithiúnas sa chás .
ó na neithib sin ; gur fhaom a ghabáil do na glantsluagaib arna
Nach rachainn ' un cainte léi .
Saol na TuaitheStair agus AiltireachtAn Parlús
Throid teaghlach na Hapsburg ( na hImpirí Ferdinand II agus III agus Pilib IV na Spáinne ) le namhaid idirnáisiúnta éagsúla , ina measc fórsaí na Fraince , na Sualainne , na Danmhairge agus na hÍsiltíre .
Rated 5 out of 5 stars 1 léirmheas ó úsáideoirí 706 úsáideoir
Bhunaigh na Proinsiasaigh mainistir sa Chabhán ag an am céanna ach níl fágtha de sin anois ach túr an chloig .
```

The below are just some checks to make sure that the only difference to the pre-training files was the changing of the conll17 tokenisation procedure. Here we see we the raw text files and `TFRecords` still are the same size:

```
# bugged
(base) jbarry@g001:~/spinning-storage/jbarry/ga_BERT/wiki-bert-pipeline/data/conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8-conll17-tokenization-bug-backup/ga/filtered-texts$ du -ch conll17_*  | grep total
112M    total

(base) jbarry@g001:~/spinning-storage/jbarry/ga_BERT/wiki-bert-pipeline/data/conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8-conll17-tokenization-bug-backup/ga/tfrecords/seq-128$ du -ch conll17_*  | grep total
2.3G    total

# bug fix
(opusfilter) jbarry@g102:~/spinning-storage/jbarry/ga_BERT/wiki-bert-pipeline/data/conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8/ga/filtered-texts$ du -ch conll17_*  | grep total
122M    total

(opusfilter) jbarry@g102:~/spinning-storage/jbarry/ga_BERT/wiki-bert-pipeline/data/conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8/ga/tfrecords/seq-128$ du -ch conll17_*  | grep total
2.3G    total
```
The below compares md5sums of the conll17 and gdrive data (other sources are not listed for space reasons but they are the same files). Notice that the conll17 files are different but gdrive are the same. There are also more conll17 files in the bugged version (due to the increased number of sentences from the tokenisation bug).

```
# bugged
(base) jbarry@g001:~/spinning-storage/jbarry/ga_BERT/wiki-bert-pipeline/data/conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8-conll17-tokenization-bug-backup/ga/tfrecords/seq-128$ md5sum *
3ad706cea7bfa4fb2ba298c9a3d7edce  conll17_00.tfrecord
1cc7fc33328abca9a6825865fda22999  conll17_01.tfrecord
758b23b9e0f22d41be6c64f3f4c8b55c  conll17_02.tfrecord
ae0eb7248cb58e6226de24063d846956  conll17_03.tfrecord
511ad85a6ae3cd4b89f89fbaf7ffb7d7  conll17_04.tfrecord
840f41792528e69fd0f2b7b0ff73cc8b  conll17_05.tfrecord
b072a5477c855e6a49e4351d13928f59  conll17_06.tfrecord
d01c2123d7126b2e9f6cc527e4a4b4c1  conll17_07.tfrecord
f94cda75a1d3b8e8f57376d80fc8a90f  conll17_08.tfrecord
19d0fc941dde103bf1d4a3c27ecacf6e  conll17_09.tfrecord
28bcb0434de3a18d0007c0fb848dfcc6  conll17_10.tfrecord
663b73e3bff67bcdfc1589ac53634a25  conll17_11.tfrecord
03694ef6a8c22794830f11ad4c6b527c  conll17_12.tfrecord
b90f125423036bad65d0a384f78b3c6d  conll17_13.tfrecord
52660f967de0a6f5aaef4e51f5cd8700  conll17_14.tfrecord
b2a116a17e9bd8881b3f95e081e71e8d  conll17_15.tfrecord
4145e374bb67afc2aa87d9ac0e3e8016  conll17_16.tfrecord
0ecc1aa07f8f8a432a542482a0431162  conll17_17.tfrecord
0e3e62d9cb14fab6922ca9841aadd5ab  conll17_18.tfrecord
3f755b4e2367aefd64b11c16d9850fcc  gdrive_00.tfrecord
7c6831105431060f833e4e202934efed  gdrive_01.tfrecord
f3ba3d82117c96c32e0781f61d7e6116  gdrive_02.tfrecord
4d50cb424d45a73c98bf40a2778d9c26  gdrive_03.tfrecord
82809e91c6ed04760b068b31d3b488a6  gdrive_04.tfrecord
c0f16d4d59d594a8018ab0b844a15122  gdrive_05.tfrecord
4b900b2d656c5afd23a2f14c99789b7c  gdrive_06.tfrecord
f38f932e6848cedf48e4e8b442e94d7a  gdrive_07.tfrecord
e66acef8959d4e8f0840e899e5ab1773  gdrive_08.tfrecord
d36bfb73b30bbaa97da73d1ea4612afc  gdrive_09.tfrecord
0aa7363e6ccec94088e586870018fb97  gdrive_10.tfrecord
7721609f83e10158600b1709808956ca  gdrive_11.tfrecord
58db4ce3ab63aed5389863f4745d83b7  gdrive_12.tfrecord

# bug fix
(base) jbarry@g001:~/spinning-storage/jbarry/ga_BERT/wiki-bert-pipeline/data/conll17_gdrive_NCI_oscar_paracrawl_filtering_basic+char-1.0+lang-0.8/ga/tfrecords/seq-128$ md5sum *
754cce03bd9ed1277bda69b6d978dd88  conll17_00.tfrecord
980e2db08ed6ebe0eb1e28cac9e722b2  conll17_01.tfrecord
2fcf1cce663e97c6b4e7153951e1f89c  conll17_02.tfrecord
e956bcfb8c3a966439c95f24eb886699  conll17_03.tfrecord
41ce5635c25874c0b78dc548a3d67586  conll17_04.tfrecord
1acd731ef77c783031b8995b5557da15  conll17_05.tfrecord
d76c0dd440e62f44ab0e9bfaa58e6bac  conll17_06.tfrecord
769a130de12a4dae28bbaa6ed349d04b  conll17_07.tfrecord
e2ff61ce0c4bb9ec2e3ad7cfeff758e4  conll17_08.tfrecord
76de5146b7a8b2bf9ddaf5edf46d7a31  conll17_09.tfrecord
4f91d1005f545039ae43a240d94ef766  conll17_10.tfrecord
f33c9076cd909d5ed457711ab0d043f0  conll17_11.tfrecord
ed6ec1d5dfb35149ef7efc85b1482e32  conll17_12.tfrecord
2771496f8416b1064aa9b179cbb1a739  conll17_13.tfrecord
8b39057b1343bbfbe513c1514641ce62  conll17_14.tfrecord
63661ee8e4b124dc4cc58ee5be7efae0  conll17_15.tfrecord
959095abef3bc2e342d6a07d5071b855  conll17_16.tfrecord
3f755b4e2367aefd64b11c16d9850fcc  gdrive_00.tfrecord
7c6831105431060f833e4e202934efed  gdrive_01.tfrecord
f3ba3d82117c96c32e0781f61d7e6116  gdrive_02.tfrecord
4d50cb424d45a73c98bf40a2778d9c26  gdrive_03.tfrecord
82809e91c6ed04760b068b31d3b488a6  gdrive_04.tfrecord
c0f16d4d59d594a8018ab0b844a15122  gdrive_05.tfrecord
4b900b2d656c5afd23a2f14c99789b7c  gdrive_06.tfrecord
f38f932e6848cedf48e4e8b442e94d7a  gdrive_07.tfrecord
e66acef8959d4e8f0840e899e5ab1773  gdrive_08.tfrecord
d36bfb73b30bbaa97da73d1ea4612afc  gdrive_09.tfrecord
0aa7363e6ccec94088e586870018fb97  gdrive_10.tfrecord
7721609f83e10158600b1709808956ca  gdrive_11.tfrecord
58db4ce3ab63aed5389863f4745d83b7  gdrive_12.tfrecord
```


### Comparison of Multi-task Dependency Parser With and Without Tokenisation Fix

The below results compare LAS, Morph. feats accuracy, POS accuracy and XPOS accuracy predicted by a multitask model using the ga_BERT checkpoint at 500,000 pretraining steps - one with the conll17 tokenisation bug and one without:

<img src="/assets/images/ga_BERT_conll17_tokenisation_dependencies_LAS.png" style="display: block; margin: 0 auto" />

<img src="/assets/images/ga_BERT_conll17_tokenisation_feats_accuracy.png" style="display: block; margin: 0 auto" />

<img src="/assets/images/ga_BERT_conll17_tokenisation_upos_accuracy.png" style="display: block; margin: 0 auto" />

<img src="/assets/images/ga_BERT_conll17_tokenisation_xpos_accuracy.png" style="display: block; margin: 0 auto" />


