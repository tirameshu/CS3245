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

def add_norm_w_and_df(docID, dictionary, docLengths, to_dict):
    docL = docLengths[docID]
    for term in dictionary:
        docs = dictionary[term]
        df = len(docs)
        if docID in docs:
            tf, weighted_tf = docs[docID]
            norm_w = weighted_tf / docL
            docs[docID].append(norm_w)

        to_dict[term] = [df]

"""
1) re-format dict
2) sort the postings for every term and take top 10 norm_w
"""
def process_dict(dictionary):
    champion_dict = {}
    posting_dict = {}
    for term in dictionary:
        doc_info = dictionary[term]
        lst = []
        for docID in doc_info:
            term_freq, weighted_tf, norm_w, df = doc_info[docID]
            t = (docID, term_freq, norm_w)
            lst.append(t)

        posting_dict[term] = lst # all postings

        ranked_norm_w = list(set(map(lambda x:x[2], lst))) # get a list of all norm_w
        ranked_norm_w.sort(reverse=True) # rank them
        champion_dict[term] = list(filter(lambda x: x[2] >= ranked_norm_w[9], lst)) # get those with norm_w >= 10th highest norm_w

    return posting_dict, champion_dict

def write_to_output(file, output_dict, to_dict):
    for term in output_dict:
        pointer = file.tell()
        docs = output_dict[term]
        pickle.dump(docs, file)

        # all terms would have alr been added in add_norm_w_and_df
        to_dict[term].append(pointer)

    file.close()

def write_to_dict(dict_file, docLengths, to_dict):
    pickle.dump(docLengths, dict_file)
    pickle.dump(to_dict, dict_file)
    dict_file.close()

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
    docLengths = {} # needs to be dictionary as file no not necessarily increment by 1
    to_dict = {}

    """
    dictionary = {
    term1: 
        {docID1: [term_freq1, weighted_tf1, norm_w1, df1]
         docID2: [term_freq2, weighted_tf2, norm_w2, df2]
         ...
        }
    ...
    }
    
    to_dict = {
    term1: {[df1, pointer_to_posting1, pointer_to_champion1]}
    term2: {[df2, pointer_to_posting2, pointer_to_champion2]}
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

            """
            add tf
            """
            if term in dictionary:
                docs = dictionary[term] # list of int docIDs
                if docID not in docs:
                    docs[docID] = [1] # first instance of this term in this doc
                else:
                    docs[docID][0] += 1 # increment tf by 1
            else:
                dictionary[term] = {docID: [1]} # first instance of term in any doc

            # print(list(dictionary.items())[:4])

        """
        docLengths updated here, weighted_tf added
        """
        docLengths[docID] = get_docL_from_weighted_tf(docID, dictionary)

        """
        norm_w, df added
        """
        add_norm_w_and_df(docID, dictionary, docLengths)

    dict_file = open(out_dict, "wb+")
    posting = open(out_postings, "wb+")
    champion_file = open("champion_list.txt", "wb+")

    new_limit = 30000
    sys.setrecursionlimit(new_limit)

    """
    reformat dictionary to 2 output formats:
    - normal posting
    - champion list
    
    to_dict is updated with the df of each term
    """
    posting_dict, champion_dict = process_dict(dictionary)

    write_to_output(posting, posting_dict, to_dict)
    write_to_output(champion_file, champion_dict, to_dict)
    write_to_dict(dict_file, docLengths, to_dict)

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
