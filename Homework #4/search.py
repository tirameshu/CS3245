import re
import sys
import getopt
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import time
import math
import pickle
import heapq

from searching_utils import parse_query, evaluate_query


def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q query-file -o output-file-of-results")

"""
For query containing AND: we will first merge the posting lists of
all query tokens, then conduct zone-scoring.

As such, regardless of boolean search or free text search or phrasal search,
zone-scoring only takes in 1 list of nodes, which is already the list of docIDs
to return to user.

This step is just to rank the docIDs. 

:param nodes: a list of Nodes already retrieved based on query

:return scores: a dictionary of { docID: zone_score }
"""
# def get_zone_score(nodes):
#     scores = {}
#     for i in range (len(nodes)):
#         node = nodes[i]
#         scores[node.docID] = get_weighted_zone(node, zone_weights)
#
#     # need sort by score
#     return scores

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    Runs search by extracting query from query file, evaluating it, and writing the results to result file

    @param dict_file the file containing dictionary written in disk
    @param postings_file the file containing postings written in disk
    @param queries_file the file containing the query
    @param results_file the file to write the results to
    """
    # load contents from dictionary saved to disk
    with open(dict_file, 'rb') as dict:
        # retrieve document lengths and vocabulary
        doc_lengths = pickle.load(dict)
        dictionary = pickle.load(dict) # contains a list of Term objects
        metadata = pickle.load(dict)

    with open(queries_file, 'r') as query_file:
        query_content = query_file.read().splitlines()
        query = query_content[0] # first line in query file is the query

        # evaluate query to obtain results
        parsed_query = parse_query(query)

        # returned result will be alr ranked:
        # free text: ranked by VSM
        # non-boolean phrase: ranked by tf of phrase
        #
        results = evaluate_query(parsed_query, dictionary, doc_lengths, postings_file)

        result_string = " ".join(str(i) for i in results)
        # TODO order relevant documents by processing metadata

    with open(results_file, 'w') as result_file:
        result_file.write(result_string + '\n')

dictionary_file = postings_file = query_file = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        query_file = a
    elif o == '-o':
        output_file_of_results = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or query_file == None or output_file_of_results == None :
    usage()
    sys.exit(2)

start_time = time.time()  # clock the run
run_search(dictionary_file, postings_file, query_file, output_file_of_results)
end_time = time.time()
print('search completed in ' + str(round(end_time - start_time, 2)) + 's')
