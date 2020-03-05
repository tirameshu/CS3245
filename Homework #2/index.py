#!/usr/bin/python3
import re
import sys
import getopt
import os
import pickle
import math

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer


class Node:
    def __init__(self, docID):
        self.docID = docID # int
        self.skip = None
        self.next = None

    def set_next(self, node):
        self.next = node

    def set_skip(self, node):
        self.skip = node

    def get_next(self):
        return self.next

    def get_skip(self):
        if (self.has_skip):
            return self.skip

    def has_next(self):
        return self.next != None and type(self.next) == Node

    def has_skip(self):
        return self.skip != None and self.skip != self


def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def setup_skip_pointers(dictionary, term):
    docs = dictionary[term] # nodes
    docs.sort(key=lambda x: x.docID)

    doc_freq = len(docs)
    sqrt_L = math.floor(math.sqrt(doc_freq))

    for i in range(doc_freq):
        node = docs[i]
        if i % sqrt_L == 0: # only for multiples of sqrt_L
            skip_to = docs[min(i+sqrt_L, doc_freq-1)]
            if skip_to != node:
                node.set_skip(skip_to)

        # set next
        if i == doc_freq-1:
            return # only last one has no next
        next = docs[i+1]
        node.set_next(next)

    dictionary[term] = docs

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
    term1: node(docID1), node(docID2), ...
    ...
    }
    """

    for docID in files:
        node = Node(docID)

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
            word = word.lower() # case folding

            if word in dictionary:
                docs = dictionary[word] # list of int docIDs
                if node not in docs:
                    docs.append(node)
            else:
                dictionary[word] = [node]

            # print(list(dictionary.items())[:4])

    # store in dict: term, docfreq, tell() in postings
    # will  write into this file directly and only once
    dict_file = open(out_dict, "w+")
    posting = open(out_postings, "wb+")

    # save a list of all file numbers to facilitate NOT search
    dict_file.write(" ".join(map(lambda x: str(x), files)))
    dict_file.write("\n")

    # print("limit: " + str(sys.getrecursionlimit()))
    new_limit = 30000
    sys.setrecursionlimit(new_limit)

    for term in dictionary:
        # sort posting and set up skip pointers first
        setup_skip_pointers(dictionary, term)

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
