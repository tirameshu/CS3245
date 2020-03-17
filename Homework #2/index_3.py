#!/usr/bin/python3
import re
import sys
import getopt
import os
import pickle
import math

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer


def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

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

    dictionary = {} # dict of term: nodes

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

            if term in dictionary:
                docs = dictionary[term] # list of int docIDs
                if docID not in docs:
                    docs[docID] = [1] # first instance of this term in this doc
                else:
                    docs[docID][0] += 1 # increment tf by 1
            else:
                dictionary[term] = {docID: [1]} # first instance of term in any doc

            # print(list(dictionary.items())[:4])

        # calculating tf:
        calculate_weighted_tf(docID)

    # store in dict: term, docfreq, tell() in postings
    # will  write into this file directly and only once
    dict_file = open(out_dict, "w+")
    posting = open(out_postings, "wb+")

    new_limit = 30000
    sys.setrecursionlimit(new_limit)

    for term in dictionary:

        # TODO: process before dumping

        pointer = posting.tell()
        # writing into postings.txt
        docs = dictionary[term]
        pickle.dump(docs, posting)

        # writing into dictionary.txt
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
