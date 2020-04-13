#!/usr/bin/python3
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
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

"""
@:param tokens: a list of all tokens
@:return positional indexs

The first time a term is encountered already
adds all positions for that doc to index.
"""

def populate_index(index, tokens, docID):
    # TODO: consider adding count as well?

    for token in tokens:
        index[docID] = set(i for i in tokens if tokens[i] == token)

def write_to_disk(index, out_dict, out_postings):
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

    data = read_csv(in_dir)

    # use Porter stemmer for stemming
    stemmer = PorterStemmer()

    # every field has its own dictionary
    title_dic = {}
    content_dic = {}
    date_dic = {}
    court_dic = {}

    for entry in data:
        docID, title, content, date, court = entry

        title_dic[docID] = title
        date_dic[docID] = date
        court_dic[docID] = court

        tokens = []

        # process content as per normal

        sentences = sent_tokenize(content)

        for sentence in sentences:
            tokens.extend([stemmer.stem(token.lower()) for token in word_tokenize(sentence)])

        populate_index(content_dic, tokens, docID)

    # restructure index and write both dictionary and postings to disk
    write_to_disk(content_dic, out_dict, out_postings)

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