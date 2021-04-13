#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) 2019 Dublin City University
# All rights reserved. This material may not be
# reproduced, displayed, modified or distributed without the express prior
# written permission of the copyright holder.

# Author: Joachim Wagner

from __future__ import print_function

import hashlib
import os
import random
import string
import sys

import basic_dataset
import conllu_dataset

def print_usage():
    print('Usage: %s [options]' %(os.path.split(sys.argv[0])[-1]))
    print("""
Processes conllu data from stdin and output tokenised text.
Options:
    --min-length  NUMBER    Only copy sentences with at least NUMBER tokens
                            (not containing tokens with an index containing
                            '.' or '-')
                            (Default: 0 = no limit)
    --max-length  NUMBER    Only copy sentences with at most NUMBER tokens
                            (not containing tokens with an index containing
                            '.' or '-')
                            (Default: 0 = no limit)
    --pass  NUMBER_1
    --passes NUMBER_2       Randomly partition data into NUMBER_2 partitions
                            and output only sentences belonging to partition
                            NUMBER_1 (indexed from 1).
                            The same --init-seed and --passes settings must
                            be used for partitions to be disjoint.
                            (Default: 1 and 1, i.e. output all data)
    --init-seed  STRING     Initialise random number generator for stochastic
                            partitioning with STRING.
                            (Default: 42)
    --prefix  STRING        Prefix each output line with STRING
                            (Default: no prefix)
    --random-prefix         Prefix each output line with a random string of
                            letters and digits and a tab
    --info  STRING          No change of behaviour. Can be used to add
                            information to the command line viewed e.g. in
                            top/htop.
""")

def main():
    opt_help = False
    opt_verbose = False
    opt_debug   = False
    opt_min_length = 0
    opt_max_length = 0
    opt_pass = 1
    opt_num_passes = 1
    opt_init_seed = '42'
    opt_prefix = ''
    opt_random_prefix = False
    while len(sys.argv) >= 2 and sys.argv[1][:1] == '-':
        option = sys.argv[1]
        option = option.replace('_', '-')
        del sys.argv[1]
        if option in ('--help', '-h'):
            opt_help = True
            break
        elif option == '--info':
            del sys.argv[1]
        elif option == '--pass':
            opt_pass = int(sys.argv[1])
            del sys.argv[1]
        elif option in ('--passes', '--num-passes'):
            opt_num_passes = int(sys.argv[1])
            del sys.argv[1]
        elif option == '--min-length':
            opt_min_length = int(sys.argv[1])
            del sys.argv[1]
        elif option == '--max-length':
            opt_max_length = int(sys.argv[1])
            del sys.argv[1]
        elif option == '--init-seed':
            opt_init_seed = sys.argv[1]
            del sys.argv[1]
        elif option == '--prefix':
            opt_prefix = sys.argv[1]
            del sys.argv[1]
        elif option == '--random-prefix':
            opt_random_prefix = True
        elif option == '--verbose':
            opt_verbose = True
        elif option == '--debug':
            opt_debug = True
        else:
            print('Unsupported or not yet implemented option %s' %option)
            opt_help = True
            break

    if len(sys.argv) != 1:
        opt_help = True

    if opt_help:
        print_usage()
        sys.exit(0)

    if opt_random_prefix and opt_prefix:
        raise ValueError('Cannot combine --prefix with --random-prefix')

    # For why using sha512, see Joachim's answer on
    # https://stackoverflow.com/questions/41699857/initialize-pseudo-random-generator-with-a-string
    random.seed(int(hashlib.sha512(opt_init_seed).hexdigest(), 16))

    max_length = opt_min_length

    if opt_random_prefix:
        index = 0
        letters = string.ascii_letters + string.digits
        k = len(letters)
    while True:
        conllu = conllu_dataset.ConlluDataset()
        sentence = conllu.read_sentence(sys.stdin)
        if sentence is None:
            break
        if random.randint(1, opt_num_passes) != opt_pass:
            continue
        length = len(sentence)
        if opt_min_length and length < opt_min_length:
            continue
        if opt_max_length and length < opt_max_length:
            continue
        tokens = []
        for item in sentence:
            tokens.append(item[1])
        sentence = ' '.join(tokens)
        if opt_random_prefix:
            opt_prefix = hashlib.sha224('%d:%s:%s:%s' %(
                index,
                ''.join(random.sample(letters, k=k)),
                opt_init_seed,
                sentence,
            )).hexdigest() + '\t'
            index += 1
        print(opt_prefix + sentence)

if __name__ == "__main__":
    main()
