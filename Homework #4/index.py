#!/usr/bin/python3
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import sys
import getopt
from pathlib import Path
import linecache
import pickle
import math
import csv

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def populate_index(index, tokens, docID):
    pass

def write_to_disk(index, doc_lengths, out_dict, out_postings):
    pass

"""
Reads a csv file and returns a list of list
containing rows in the csv file and its entries,
including header row.
"""
def read_csv(csvfilename):
    rows = []

    with open(csvfilename) as csvfile:
        file_reader = csv.reader(csvfile)
        for row in file_reader:
            rows.append(row)
    return rows

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory, then output the dictionary file and postings file.
    @param in_dir input file specifying the directory containing the corpus of documents
    @param out_dict output file for the dictionary to be written to
    @param out_postings output file for postings lists to be written to
    """
    print('indexing...')

    # obtain file paths of documents to be indexed
    file_paths = [f for f in Path(in_dir).iterdir() if f.is_file()]

    # initialise dictionaries to store vocabulary and document lengths
    index = {}
    doc_lengths = {}

    # use Porter stemmer for stemming
    stemmer = PorterStemmer()

    for file in file_paths:
        # extract and save document ID
        docID = int(file.stem)

        print("indexing doc " + str(docID)) # for debugging

        # list of tokens in current document
        tokens = []

        # get all lines from the current document
        lines = linecache.getlines(str(file))

        # case folding, word tokenizing, stemming
        for line in lines:
            tokens.extend([stemmer.stem(token.lower()) for token in word_tokenize(line)])

        # add distinct words to the index while storing doc ID and term frequency
        # method returns document length as well
        doc_length = populate_index(index, tokens, docID)

        # store document length
        doc_lengths[docID] = doc_length

    # restructure index and write both dictionary and postings to disk
    write_to_disk(index, doc_lengths, out_dict, out_postings)

    print("done indexing")

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