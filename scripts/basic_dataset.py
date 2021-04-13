#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) 2019 Dublin City University
# All rights reserved. This material may not be
# reproduced, displayed, modified or distributed without the express prior
# written permission of the copyright holder.

# Author: Joachim Wagner

from __future__ import print_function

import bz2
import collections
import hashlib
import random
import sys
import time

# https://stackoverflow.com/questions/11914472/stringio-in-python3
try:
    from StringIO import StringIO ## for Python 2
except ImportError:
    from io import StringIO ## for Python 3

class Sentence(collections.Sequence):

    def __init__(self):
        pass

    def __getitem__(self, index):
        raise NotImplementedError

    def collect_labels(self, labelset, column):
        ''' For each label in the given column, add the
            label as a key to the dictionary `labelset`
        '''
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError

    def append(self, line):
        raise NotImplementedError

    def clone(self):
        raise NotImplementedError

    def is_missing(self, index, column):
        return False

    def set_label(self, index, column, new_label):
        raise NotImplementedError

    def possible_labels(self, index, column):
        raise NotImplementedError

    def unset_label(self, index, column):
        raise NotImplementedError

    def get_vector_representation(self):
        raise NotImplementedError


class Dataset(collections.Sequence):

    """ Abstract base class for data sets.
    """

    def __init__(self):
        self.sentences = []    # see __getitem__() below for format
        self.files = []
        self.load_kwargs = {}

    def __getitem__(self, index):
        f_index, info = self.sentences[index]
        if f_index < 0:
            return info
        else:
            f_in = self.files[f_index]
            f_in.seek(info)
            return self.read_sentence(f_in)

    def collect_labels(self, labelset, column):
        for sentence in self:
            sentence.collect_labels(labelset, column)

    def __len__(self):
        return len(self.sentences)

    def clone(self):
        retval = Dataset()
        # make new lists so that shuffling the clone
        # does not affect self
        retval.sentences = self.sentences[:]
        retval.files = self.files[:]
        return retval

    def append(self, sentence):
        self.sentences.append((-1, sentence))

    def shuffle(self, rng):
        rng.shuffle(self.sentences)

    def load_file(self, f_in, max_sentences = None, **kwargs):
        """ Append up to `max_sentences` sentences from file `f_in`
            to the data set. No limit if `max_sentences` is `None`.
        """
        self.load_or_map_file(f_in, max_sentences, 'load', **kwargs)

    def map_file(self, f_in, max_sentences = None, **kwargs):
        """ Append up to `max_sentences` sentences from file `f_in`
            to the data set. No limit if `max_sentences` is `None`.
            The file is scanned for start positions of sentences
            and only references are stored in memory. Data will be
            re-read each time it is needed. The file must not be
            modified or closed while it is mapped.
        """
        self.load_or_map_file(f_in, max_sentences, 'map', **kwargs)

    def load_or_map_file(self, f_in, max_sentences, mode, **kwargs):
        self.load_kwargs = kwargs
        if mode == 'map':
            f_index = len(self.files)
            self.files.append(f_in)
        else:
            f_index = -1
        added = 0
        while True:
            if max_sentences is not None and added == max_sentences:
                break
            if mode == 'map':
                info = f_in.tell()
            sentence = self.read_sentence(f_in)
            if not sentence:
                break
            if mode == 'load':
                info = sentence
            if not self.usable(sentence, **kwargs):
                continue
            self.sentences.append((f_index, info))
            added += 1
        return added

    def usable(self, sentence, **kwargs):
        return True

    def save_to_file(self, f_out,
        sentence_filter    = None,
        sentence_completer = None,
        remove_comments    = False,
    ):
        for sentence in self:
            if sentence_filter is not None \
            and sentence_filter(sentence):
                # skip this sentence
                continue
            if sentence_completer is not None:
                sentence = sentence_completer(sentence)
            self.write_sentence(f_out, sentence, remove_comments)

    def hexdigest(self):
        h = hashlib.sha512()
        for sentence in self:
            f = StringIO()
            self.write_sentence(f, sentence, remove_comments = True)
            f.seek(0)
            h.update(f.read())
        return h.hexdigest()

    def read_sentence(self, f_in):
        raise NotImplementedError

    def write_sentence(self, f_out, sentence, remove_comments = False):
        raise NotImplementedError

    def get_number_of_items(self):
        count = 0
        for sentence in self:
            count += len(sentence)
        return count


class SentenceCompleter:

    def __init__(self, rng, target_columns, target_labelsets):
        self.rng = rng
        self.target_columns = target_columns
        self.target_labelsets = target_labelsets

    def pick_label(self, sentence, item_index, tc_index, column):
        labelset = self.target_labelsets[tc_index]
        if not labelset:
            labelset = sentence.possible_labels(item_index, column)
        return self.rng.choice(labelset)

    def __call__(self, sentence):
        retval = None
        for item_index in range(len(sentence)):
            for tc_index, column in enumerate(self.target_columns):
                if sentence.is_missing(item_index, column):
                    if not retval:
                        retval = sentence.clone()
                    new_label = self.pick_label(
                        sentence, item_index, tc_index, column
                    )
                    retval.set_label(item_index, column, new_label)
        if not retval:
            return sentence
        return retval


class SentenceDropout:

    def __init__(self, rng, target_columns, dropout_probabilities):
        self.rng = rng
        self.target_columns = target_columns
        self.dropout_probabilities = dropout_probabilities

    def __call__(self, sentence):
        retval = sentence.clone()
        for item_index in range(len(sentence)):
            for tc_index, column in enumerate(self.target_columns):
                dropout_probability = self.dropout_probabilities[tc_index]
                if self.rng.random() < dropout_probability:
                    retval.unset_label(item_index, column)
        return retval


class SentenceFilter:

    def __init__(self, target_columns,
        min_labelled = None, max_unlabelled = None,
        min_percentage_labelled = None,
        max_percentage_unlabelled = None,
        min_length = None, max_length = None,
        skip_prob = 0.0, rng = None,
    ):
        self.target_columns = target_columns
        self.min_labelled   = min_labelled
        self.max_unlabelled = max_unlabelled
        self.min_percentage = min_percentage_labelled
        self.max_percentage = max_percentage_unlabelled
        self.min_length     = min_length
        self.max_length     = max_length
        self.skip_prob      = skip_prob
        self.rng            = rng

    def __call__(self, sentence):
        ''' returns True if the sentence should be skipped '''
        if self.skip_prob and self.rng.random() < self.skip_prob:
            return True
        num_items = len(sentence)
        if self.min_length and num_items < self.min_length:
            return True
        if self.max_length and num_items > self.max_length:
            return True
        for tc_index, column in enumerate(self.target_columns):
            num_labelled = 0
            for item_index in range(num_items):
                if not sentence.is_missing(item_index, column):
                    num_labelled += 1
            if self.min_labelled \
            and num_labelled < self.min_labelled[tc_index]:
                return True
            num_unlabelled = num_items - num_labelled
            if self.max_unlabelled \
            and num_unlabelled > self.max_unlabelled[tc_index]:
                return True
            percentage = 100.0 * num_labelled / float(num_items)
            if self.min_percentage \
            and percentage < self.min_percentage[tc_index]:
                return True
            percentage = 100.0 * num_unlabelled / float(num_items)
            if self.max_percentage \
            and percentage > self.max_percentage[tc_index]:
                return True
        return False


class Concat(Dataset):

    def __init__(self, datasets, sentence_modifier = None):
        self.datasets = datasets
        self.sentence_modifier = sentence_modifier
        self.sentences = []
        for ds_index, dataset in enumerate(datasets):
            if dataset is None:
                continue
            for d_index in range(len(dataset)):
                self.sentences.append((ds_index, d_index))

    def __getitem__(self, index):
        ds_index, d_index = self.sentences[index]
        sentence = self.datasets[ds_index][d_index]
        if self.sentence_modifier is not None:
            sentence = self.sentence_modifier(sentence)
        return sentence

    def clone(self):
        retval = Concat([])
        # make new lists so that shuffling the clone
        # does not affect self
        retval.sentences = self.sentences[:]
        retval.datasets = self.datasets[:]
        retval.sentence_modifier = self.sentence_modifier
        return retval

    def append(self, item):
        raise ValueError('Cannot append to concatenation')

    def load_or_map_file(self, *args):
        raise ValueError('Cannot load data into concatenation')

    def write_sentence(self, f_out, sentence, remove_comments = False):
        self.datasets[0].write_sentence(f_out, sentence, remove_comments)


class Sample(Dataset):

    def __init__(self, dataset, rng, size = None, percentage = None,
        with_replacement = True,
        unique_sentences = False,
        sentence_modifier = None,
        sentence_filter   = None,
        diversify_attempts = 1,
        disprefer = {},
        stratified = False,
        keep_order = False,
    ):
        if size and percentage:
            raise ValueError('Must not specify both size and percentage.')
        if percentage:
            size = int(0.5+percentage*len(dataset)/100.0)
        self.dataset = dataset
        self.is_vectorised = False
        self.sentence_modifier = sentence_modifier
        self.sentence_filter   = sentence_filter
        self.with_replacement  = with_replacement
        self.keep_order        = keep_order
        self.reset_sample(
            rng, size, diversify_attempts, disprefer,
            unique_sentences,
            stratified,
        )

    def _get_preferred_d_indices(self, d_size, size, disprefer, stratified = False):
        ''' size is the target size,
            d_size is the size of the existing dataset
        '''
        if size >= d_size or not disprefer:
            # use all data
            return list(range(d_size)), []
        # stratify data according to
        # how strongly items are dispreferred
        level2indices = {}
        max_level = 0
        for d_index in range(d_size):
            try:
                level = disprefer[d_index]
            except KeyError:
                level = 0
            if level not in level2indices:
                level2indices[level] = []
            level2indices[level].append(d_index)
            if level > max_level:
                max_level = level
        # select as much data as needed
        # starting with the lowest levels
        retval = []
        if stratified:
            # make sure the first and only iteration of the while loop
            # below when stratified is true adds at least 1 item to
            # retval
            level = min(level2indices.keys())
        else:
            level = 0
        # TODO: when filtering and/or rejecting duplicates, we may need
        #       more data but currently we are shuffling the data after
        #       calling this function, meaning that we must not return
        #       more data
        while len(retval) < size:
            assert level <= max_level, 'Missing some data after stratification.'
            try:
                indices = level2indices[level]
            except KeyError:
                indices = []
            retval += indices
            level += 1
            if stratified:
                break
        extra_data = []
        while level <= max_level:
            try:
                indices = level2indices[level]
            except KeyError:
                indices = []
            if stratified and indices:
                extra_data.append(indices)
            else:
                extra_data += indices
            level += 1
        if not stratified:
            new_extra_data = []
            new_extra_data.append(extra_data)
            extra_data = new_extra_data
        return retval, extra_data

    def reset_sample(
        self, rng, size = None,
        diversify_attempts = 1,
        disprefer = {},
        unique_sentences = False,
        stratified = False,
    ):
        if self.with_replacement and disprefer:
            # not clear how this should be implemented,
            # e.g. with what probability dispreferred
            # items should be picked
            raise NotImplementedError
        if self.keep_order and self.with_replacement:
            # this could be implemented by recording
            # the original index when sampling and
            # sorting the sample when finished
            raise NotImplementedError
        d_size = len(self.dataset)
        if size is None:
            size = d_size
        if unique_sentences and size > d_size:
            raise ValueError('Cannot make larger sample than given data without duplicating items')
        if not self.with_replacement:
            permutation, extra_data = self._get_preferred_d_indices(
                d_size, size, disprefer, stratified
            )
            p_size = len(permutation)
            if not self.keep_order:
                rng.shuffle(permutation)
        else:
            p_size = -1
            extra_data = []
        print('Sampling %s: %d target size, %d dataset size, %d permutation size, stratified is %r, %d dispreferred items, %d diversify_attempts, unique_sentences is %r, %d extra strata available' %(
            time.ctime(time.time()), size, d_size, p_size,
            stratified,
            len(disprefer), diversify_attempts, unique_sentences,
            len(extra_data)
        ), file=sys.stderr)
        self.sentences = []
        remaining = size
        rejected = 0
        filtered = 0
        previous_attempts_offset = 0
        if unique_sentences:
            so_far = {}
        last_verbose = time.time()
        interval = 5.0
        while remaining:
            candidates = []
            for attempt in range(diversify_attempts):
                if self.with_replacement:
                    # Since we currently do not support sampling with
                    # replacement together with disprefering some items,
                    # we can simply sample from all data:
                    d_index = rng.randrange(d_size)
                else:
                    p_index = size + previous_attempts_offset + \
                              attempt + filtered + \
                              rejected - remaining
                    if extra_data and p_index >= p_size:
                        e_data = extra_data[0]
                        del extra_data[0]
                        if not self.keep_order:
                            rng.shuffle(e_data)
                        permutation += e_data
                        old_p_size = p_size
                        p_size = len(permutation)
                        print('Sampling %s: extended %d permutation size to %d' %(
                            time.ctime(time.time()), old_p_size, p_size
                        ), file=sys.stderr)
                    d_index = permutation[p_index % p_size]

                if diversify_attempts == 1 or not self.sentences:
                    # no choice
                    priority = 0
                else:
                    priority = -self._nearest_neighbour_distance(d_index)
                candidates.append((priority, attempt, d_index))
            candidates.sort()
            _, attempt, d_index = candidates[0]
            previous_attempts_offset += attempt
            self.sentences.append(d_index)
            if unique_sentences or self.sentence_filter is not None:
                if time.time() > last_verbose + interval:
                    print('Sampling %s: %d left, %d rejected, %d filtered, %d target size, %d dataset size, %d permutation size' %(
                        time.ctime(time.time()), remaining, rejected, filtered,
                        size, d_size, p_size,
                    ), file=sys.stderr)
                    sys.stdout.flush()
                    last_verbose = time.time()
                    interval *= 2.0
            if unique_sentences \
            and p_index >= p_size * (1+diversify_attempts) \
            and not self.with_replacement:
                print('Sampling %s: giving up at p_index %d' %(
                    time.ctime(time.time()), p_index,
                ), file=sys.stderr)
                break
            dispr_offset = 10 + (d_index % 10)
            if self.sentence_filter is not None:
                if self.sentence_filter(self[-1]):
                    del self.sentences[-1]
                    filtered += 1
                    if disprefer:
                        # push item far down the list but not too far as
                        # _get_preferred_d_indices() iterates over the full
                        # range(min, max) of values
                        try:
                            disprefer[d_index] += dispr_offset
                        except KeyError:
                            disprefer[d_index] = dispr_offset
                    continue
            if unique_sentences:
                # check that the new sentence is different from all so far:
                f = StringIO()
                self.write_sentence(f, self[-1], remove_comments = True)
                f.seek(0)
                candidate = hashlib.sha256(f.read()).digest()[:12]
                if candidate in so_far:
                    del self.sentences[-1]
                    rejected += 1
                    if disprefer:
                        # push item far down the list but not too far as
                        # _get_preferred_d_indices() iterates over the full
                        # range(min, max) of values
                        try:
                            disprefer[d_index] += dispr_offset
                        except KeyError:
                            disprefer[d_index] = dispr_offset
                    continue
                so_far[candidate] = None
            remaining -= 1

    def _nearest_neighbour_distance(self, d_index):
        if not self.is_vectorised:
            self._vectorise()
        nn_distance = self._vector_distance(self.sentence[0], d_index)
        for candidate_index in self.sentences[1:]:
            distance = self._vector_distance(candidate_index, d_index)
            if distance < nn_distance:
                nn_distance = distance
        return nn_distance

    def _vectorise(self):
        self.vectors = []
        for d_index, sentence in enumerate(self.dataset):
            self.vectors.append(sentence.get_vector_representation())
        self.is_vectorised = True

    def __getitem__(self, index):
        d_index = self.sentences[index]
        sentence = self.dataset[d_index]
        if self.sentence_modifier is not None:
            sentence = self.sentence_modifier(sentence)
        return sentence

    def indices(self):
        return self.sentences

    def clone(self):
        retval = Sample([], random)
        # make new lists so that shuffling the clone
        # or changing the subset with reset_sample(),
        # set_counts() or set_remaining() does not
        # affect self
        retval.sentences = self.sentences[:]
        retval.dataset = self.dataset
        retval.is_vectorised = self.is_vectorised
        if self.is_vectorised:
            retval.vectors = self.vectors
        retval.sentence_modifier = self.sentence_modifier
        retval.with_replacement  = self.with_replacement
        return retval

    def append(self, item):
        raise ValueError('Cannot append to sample')

    def load_or_map_file(self, *args):
        raise ValueError('Cannot load data into sample')

    def get_counts(self):
        retval = len(self.dataset) * [0]
        for d_index in self.sentences:
            retval[d_index] += 1
        return retval

    def set_counts(self, rng, counts):
        self.sentences = []
        for d_index, count in enumerate(counts):
            for _ in count:
                self.sentences.append(d_index)
        self.shuffle(rng)

    def set_remaining(self, rng):
        '''
        Make this dataset the subset not selected by the current sample.
        '''
        counts = self.get_counts()
        self.sentences = []
        for d_index, count in enumerate(counts):
            if not count:
                self.sentences.append(d_index)
        self.shuffle(rng)

    def write_sentence(self, f_out, sentence, remove_comments = False):
        self.dataset.write_sentence(f_out, sentence, remove_comments)


def load_or_map_from_filename(data, filename, mode = 'load', **kwargs):
    if filename.endswith('.bz2'):
        f_in = bz2.BZ2File(filename, 'r')
        if mode == 'map':
            print('Warning: opening .bz2 file in map mode: %s\n' %filename,
                file=sys.stderr,
            )
    else:
        f_in = open(filename, 'r')
    data.load_or_map_file(f_in, None, mode, **kwargs)
    if mode == 'load':
        f_in.close()
    data.filename = filename
    return data

def load(dataset_id,
    load_tr = True, load_dev = True, load_test = True,
    mode = 'load',
    dataset_basedir = None,
):
    raise NotImplementedError


def new_empty_set():
    raise NotImplementedError

def get_target_columns():
    raise NotImplementedError

def get_filename_extension():
    ''' recommended extension for output files '''
    return '.data'

def combine(prediction_paths, output_path):
    ''' combine (ensemble) the given predictions
        into a single prediction
    '''
    raise NotImplementedError

def get_filter(**kwargs):
    ''' return a sentence filter object
        (must support that numerical values can be
        provided as strings)
    '''
    raise NotImplementedError
    # TODO: convert string to int
    #return SentenceFilter([], **kwargs)