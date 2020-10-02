import opusfilter
from opusfilter import FilterABC
import string

"""
This module needs to be added to Python path:
    e.g.: export PYTHONPATH=/home/user/ga_BERT/Irish-BERT/filters/
"""


class PunctuationFilter(FilterABC):
    """Calculates the percentage of punctuation among characters of a sentence"""

    def __init__(self, threshold=0.2, **kwargs):
        self.threshold = threshold
        super().__init__(**kwargs)

    def score(self, pairs):
        """
        pairs: List[Tuple]
            A list of Tuples where each Tuple contains a sentence.
        """
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

