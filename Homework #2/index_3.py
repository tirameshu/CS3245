#!/usr/bin/python3
from __future__ import division

import re
import sys
import getopt
import os
import pickle
import math

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer


def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dic-file -p postings-file")

# add weighted_tf
def get_docL_from_weighted_tf(docID, dictionary):
    pre_docL_sum = 0
    for term in dictionary:
        docs = dictionary[term]
        if docID in docs:
            vals = docs[docID]
            tf = vals[0]
            weighted_tf = 1 + math.log(tf, 10)
            vals.append(weighted_tf)

            # calculating docL
            pre_docL_sum += weighted_tf**2

    if pre_docL_sum:
        docL = math.sqrt(pre_docL_sum)
        return docL
    else:
        print("docL should not be 0!")
        return 0

def add_norm_w_and_df(docID, dictionary, docLengths):
    docL = docLengths[docID]
    for term in dictionary:
        docs = dictionary[term]
        df = len(docs)
        if docID in docs:
            tf, weighted_tf = docs[docID]
            norm_w = weighted_tf / docL
            docs[docID].append(norm_w)
        docs[docID].append(df)

"""
1) re-format dict
2) sort the postings for every term and take top 10 norm_w
"""
def process_dict(dictionary):
    new_dict = {}
    for term in dictionary:
        doc_info = dictionary[term]
        lst = []
        for docID in doc_info:
            term_freq, weighted_tf, norm_w, df = doc_info[docID]
            t = (docID, term_freq, norm_w)
            lst.append(t)

        ranked_norm_w = list(set(map(lambda x:x[2], lst))) # get a list of all norm_w
        ranked_norm_w.sort(reverse=True) # rank them
        new_dict[term] = list(filter(lambda x: x[2] >= ranked_norm_w[9])) # get those with norm_w >= 10th highest norm_w

    return new_dict

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')

    script_abs_path = os.path.dirname(os.path.abspath(__file__))
    dir = os.path.join(script_abs_path, in_dir)

    files = os.listdir(dir)
    files = list(map(lambda x: int(x), files)) # list of int
    files.sort()

    dictionary = {}
    docLengths = []

    """
    dictionary = {
    term1: 
        {docID1: [term_freq1, docL1]
         docID2: [term_freq2, docL2]
         ...
        }
    ...
    }
    """

    for docID in files: # alr int
        docLengths.append(0) # initialise

        file = open(os.path.join(dir, str(docID)))
        sentences = sent_tokenize(file.read())
        words_nested = map(lambda x: word_tokenize(x), sentences)
        words = set() # set of all distinct words
        for unit in words_nested:
            words.update(set(unit))

        for word in words:
            if not word.isalpha():
                continue

            ps = PorterStemmer()
            word = ps.stem(word) # stemming
            term = word.lower() # case folding

            # add tf
            if term in dictionary:
                docs = dictionary[term] # list of int docIDs
                if docID not in docs:
                    docs[docID] = [1] # first instance of this term in this doc
                else:
                    docs[docID][0] += 1 # increment tf by 1
            else:
                dictionary[term] = {docID: [1]} # first instance of term in any doc

            # print(list(dictionary.items())[:4])

        docLengths[docID] = get_docL_from_weighted_tf(docID, dictionary)
        calculate_norm_w(docID, dictionary, docLengths)

    # will  write into this file directly and only once
    dict_file = open(out_dict, "w+")
    posting = open(out_postings, "wb+")

    new_limit = 30000
    sys.setrecursionlimit(new_limit)

    processed_dict = process_dict(dictionary)

    for term in processed_dict:
        pointer = posting.tell()
        # writing into postings.txt
        docs = processed_dict[term]
        pickle.dump(docs, posting)

        # writing into dic.txt
        # stores term, doc_freq, pointer
        to_dict = " ".join((term, str(len(docs)), str(pointer)))
        dict_file.write(to_dict + "\n")

    posting.close()

input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
