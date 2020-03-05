#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import nltk
import math
import sys
import getopt

langs = []
tokens = []

def get_four_gram(words):
    if len(words) == 3:
        token = words + " " # add spacing to last token
        words = ""
    else:
        token = words[:4]
        words = words[1:] # only shift by 1 letter

    return token, words

def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and a string separated by a space
    """
    print('building language models...')

    lang_tokens = {}
    token_langs = {}

    with open (in_file, 'r') as f:
        lines = f.readlines()

    #######################################################
    print('building count table...')

    for line in lines:
        index_of_first_space = line.index(" ")
        language = line[:index_of_first_space]
        words = line[index_of_first_space:] # includes first spacing

        if language not in langs:
            langs.append(language)
            lang_tokens[language] = {}

        token, words = get_four_gram(words)

        while (token):
            if token not in tokens: # first encounter of new token
                tokens.append(token)
                token_langs[token] = {}

            # first-timers do this to set up
            # others check for new language
            for lang in langs:
                if lang not in token_langs[token]:
                    token_langs[token][lang] = 1

                if token not in lang_tokens[lang]:
                    lang_tokens[lang][token] = 1

            token_langs[token][language] += 1
            lang_tokens[language][token] += 1

            token, words = get_four_gram(words)

    #####################################################
    print('building probability table...')

    p_lang_tokens = {}
    p_token_langs = {}

    for lang in langs:
        for token in tokens: # ensures that lang_tokens contain all tokens

            # some tokens appeared before new languages appeared
            if lang not in token_langs[token]:
                token_langs[token][lang] = 1

            if token not in lang_tokens[lang]:
                lang_tokens[lang][token] = 1

            token_count = lang_tokens[lang][token]
            total_count = sum(lang_tokens[lang].values())
            probability = token_count / total_count

            if lang not in p_lang_tokens:
                p_lang_tokens[lang] = {}
            p_lang_tokens[lang][token] = probability

            if token not in p_token_langs:
                p_token_langs[token] = {}
            p_token_langs[token][lang] = probability

    return p_token_langs

def test_LM(in_file, out_file, LM):
    """
    test the language models on new strings
    each line of in_file contains a string
    you should print the most probable label for each string into out_file
    """
    print("testing language models...")

    with open (in_file, 'r') as f:
        lines = f.readlines()

    of = open(out_file, 'a')

    for line in lines:
        prob_by_lang = {}

        for lang in langs:
            prob_by_lang[lang] = 0

        words = " " + line # simulate "START" token, like training set
        token, words = get_four_gram(words)

        while (token):
            if token not in tokens:
                token, words = get_four_gram(words) # move on
                continue # just skip first

            for lang in langs:
                prob_by_lang[lang] += math.log(LM[token][lang])

            token, words = get_four_gram(words)

        if not prob_by_lang: # assuming no 4-gram will match existing LM
            predicted_lang = "other"
        else:
            predicted_lang = max(prob_by_lang, key=prob_by_lang.get)

        of.write(predicted_lang + ' ' + line)

def usage():
    print("usage: " + sys.argv[0] + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file")

input_file_b = input_file_t = output_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'b:t:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-b':
        input_file_b = a
    elif o == '-t':
        input_file_t = a
    elif o == '-o':
        output_file = a
    else:
        assert False, "unhandled option"
if input_file_b == None or input_file_t == None or output_file == None:
    usage()
    sys.exit(2)

LM = build_LM(input_file_b)
test_LM(input_file_t, output_file, LM)
