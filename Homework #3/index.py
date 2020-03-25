#!/usr/bin/python3
import re
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import sys
import getopt
from pathlib import Path
import linecache
import pickle
import math

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def populate_index(index, tokens, docID):
    """
    Stores unique words in the dictionary along with their term frequency and document ID. Returns document length
    corresponding to the given docID.

    @param index dictionary that contains the index to be populated
    @param tokens list of tokens in current document
    @param docID document ID of current document
    @return float representing length of document
    """
    for token in tokens:
        if token in index:
            docs = index[token] # get dictionary of docIDs containing this term as key
            if docID not in docs:
                docs[docID] = 1 # first instance of this term in this doc
            else:
                docs[docID] += 1 # increment term frequency by 1
        else:
            index[token] = {docID: 1} # first instance of term in any doc

    words = set(tokens) # list of unique words in document with given docID
    running_total = 0
    for word in words:
        tf = index[word][docID] # get term frequency of this word
        weighted_tf = 1 + math.log(tf, 10) # tf is guaranteed to be at least 1
        running_total += weighted_tf**2 # update running total for document length calculation

    doc_length = math.sqrt(running_total)
    return doc_length

def write_to_disk(index, doc_lengths, out_dict, out_postings):
    """
    Writes dictionary and postings lists to disk using pickle.

    @param index dictionary that contains the index to be separated into dictionary and postings lists
    @param doc_lengths list of document lengths of all documents in the corpus]
    @param out_dict output file for the dictionary to be written to
    @param out_postings output file for the postings lists to be written to
    """
    dictionary = {} # key - term, value - (document_frequency, pointer_to_postings_list)

    # save postings to disk
    with open(out_postings, 'wb') as postings:
        for term, doc_info in index.items():
            # obtain postings list from index
            postings_list = []
            for docID, tf in doc_info.items():
                postings_list.append((docID, tf)) # (docID, tf)
            postings_list.sort(key=lambda x: x[0]) # sort by docID

            # populate dictionary
            df = len(postings_list) # get document frequency
            pointer = postings.tell() # get pointer
            dictionary[term] = (df, pointer)

            # store postings list to disk
            pickle.dump(postings_list, postings)


    # save dictionary to disk
    with open(out_dict, 'wb') as dict:
        pickle.dump(doc_lengths, dict)
        pickle.dump(dictionary, dict)

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
