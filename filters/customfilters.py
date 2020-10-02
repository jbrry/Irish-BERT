import opusfilter
from opusfilter import FilterABC
import string

"""
This module includes some additional filters to the OpusFilter library.
For a list of existing filters, see: https://github.com/Helsinki-NLP/OpusFilter/blob/nlingual-rebase/opusfilter/filters.py

This module needs to be added to Python path:
    e.g.: export PYTHONPATH=/home/user/ga_BERT/Irish-BERT/filters/
"""


class PunctuationFilter(FilterABC):
    """Calculates the percentage of punctuation among characters of a sentence"""

    def __init__(self, threshold=0.2, **kwargs):
        self.threshold = threshold
        super().__init__(**kwargs)

    def score(self, pairs):
        punct = set(string.punctuation)

        for pair in pairs:
            for sent in pair:
                words = sent.split()
                num_chars = len([c for w in words for c in w])
                num_punct_chars = len([c for w in words for c in w if c in punct])
                punct_ratio = num_punct_chars / num_chars
                yield punct_ratio

    def accept(self, score):
        return score < self.threshold


class DigitsFilter(FilterABC):
    """Calculates the percentage of digits among characters of a sentence"""

    def __init__(self, threshold=0.2, **kwargs):
        self.threshold = threshold
        super().__init__(**kwargs)

    def score(self, pairs):
        digits = set(string.digits)
        
        for pair in pairs:
            for sent in pair:
                words = sent.split()
                num_chars = len([c for w in words for c in w])
                num_digit_chars = len([c for w in words for c in w if c in digits])
                digit_ratio = num_digit_chars / num_chars
                yield digit_ratio

    def accept(self, score):
        return score < self.threshold
