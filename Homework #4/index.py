#!/usr/bin/python3
import csv
import getopt
import sys
import time

from indexing_utils import collect_tokens, process_tokens, calculate_doc_length, write_to_disk

def usage():
    print("usage: " + sys.argv[0] + " -i dataset-file -d dictionary-file -p postings-file")

def build_index(in_file, out_dict, out_postings):
    """
    Builds index by extracting key information from given dataset file.

    @param in_file input dataset file the index is built from
    @param out_dict target output file to write dictionary to
    @param out_postings target output file to write postings to
    """
    print('indexing...')

    # initialise a dictionary to contain the index where key is the processed token, value is a dictionary of Nodes
    # for the dictionary of Nodes, key is doc_id and value is Node
    # Node class encapsulates doc_id, positional indices (hence tf), next node, and skip node
    # We adopt Single-Pass In-Memory Indexing (SPIM) and index directly when a term is encountered
    # Correct storage of zones is contingent on SPIM
    # the "title" and "court" zones are extracted and stored in separate dictionaries
    # the "date_published" zone is deemed irrelevant and is not stored
    index = {}

    doc_lengths = {}  # dictionary to store doc_lengths, with doc_id as key and doc_length as value
    titles = {} # dictionary to store titles of all cases, with doc_id as key and title as value
    courts = {} # dictionary to store courts of all cases, with doc_id as key and court as value

    # read and process each row in csv file
    with open(in_file, 'r') as csvfile:
        file_reader = csv.DictReader(csvfile)
        for row in file_reader:
            doc_id = row["document_id"] # extract document ID
            print("indexing doc " + str(doc_id)) # for debugging

            # collect tokens in current document
            content = row["content"] # extract case content
            tokens = collect_tokens(content)

            # process all tokens to build index
            # returns a dictionary of term frequencies to calculate document length
            term_frequencies = process_tokens(index, tokens, doc_id)

            # calculate and store document length
            doc_length = calculate_doc_length([value for value in term_frequencies.values()])
            doc_lengths[doc_id] = doc_length

            # store metadata
            title = row["title"] # extract case title
            titles[doc_id] = title
            court = row["court"] # extract court
            courts[doc_id] = court

    # write both dictionary and postings to disk
    write_to_disk(index, doc_lengths, titles, courts, out_dict, out_postings)

    print("done indexing")

dataset_file = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input dataset file
        dataset_file = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if dataset_file == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

# build_index(input_directory, output_file_dictionary, output_file_postings)
start_time = time.time()  # clock the run
build_index(dataset_file, output_file_dictionary, output_file_postings)
end_time = time.time()
print('indexing completed in ' + str(round(end_time - start_time, 2)) + 's')
