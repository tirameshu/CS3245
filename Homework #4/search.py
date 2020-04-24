import re
import sys
import getopt
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import time
import math
import pickle
import heapq

from dictionary import Dictionary
from postings import Postings
from searching_utils import parse_query, evaluate_query


def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

"""
:param query: list of stemmed query tokens, phrasal searches given as a phrase without quotation but with space
"""
def boolean_search(query_tokens):
    pass

"""
:param lst1: list of Nodes from the first part of AND
:param lst2: list of Nodes from the second part of AND
"""
def and_merge(lst1, lst2):
    # first take care of edge cases
    if not lst1 and not lst2:
        return []

    if lst1 and not lst2:
        return lst1

    if lst2 and not lst1:
        return lst2

    # normal use case

    node1 = lst1[0]
    node2 = lst2[0]
    result = []

    while node1.has_skip() and node2.has_skip():
        if node1.get_doc_id() < node2.get_doc_id():
            if node1.has_skip():
                skip_node = node1.get_skip()
                if skip_node.get_doc_id() < node2.get_doc_id(): # utilise skip pointer
                    node1 = skip_node
                else:
                    node1 = node1.get_next()
            else:
                node1 = node1.get_next()

        elif node2.get_doc_id() < node1.get_doc_id():
            if node2.has_skip():
                skip_node = node2.get_skip()
                if skip_node.get_doc_id() < node1.get_doc_id():  # utilise skip pointer
                    node2 = skip_node
                else:
                    node2 = node2.get_next()
            else:
                node2 = node2.get_next()
        else:
            result.append(node1) # save node
            node1 = node1.get_next()
            node2 = node2.get_next()

    return result

"""
:param node: contains docID, positional indices, next node, skip node
fields and corresponding boolean values

:param zone_weights: weights given to each zone to be multiplied with boolean
:return zone_score: sum of zone_score for each zone
"""
def get_weighted_zone(node, zone_weights):
    """
    implementation 1: every zone contains a boolean value

    implementation 2: node has attributes "in_metadata" and "in_body",
    with boolean values for both, so calculation is only done based on these two.
    """
    # assuming implementation 2

    return node.in_metadata * zone_weights[0] + node.in_body * zone_weights[1]

"""
Assumes common document for two tokens have been found, and the corresponding postings lists are being used.

:param positions1: a list of positions for token1 in common doc
:param positions2: a list of positions for token2 in common doc
"""
def get_consecutives(positions1, positions2):
    result = []
    i, j = 0, 0
    while i < len(positions1) and j < len(positions2):
        p1 = positions1[i]
        p2 = positions2[j]

        # p2 has to be after p1
        if p2 <= p1:
            j += 1
            continue

        elif p2 - p1 == 1:
            result.append((p1, p2))

            i += 1
            j += 1

        else:
            i += 1

    return result

"""
:param query_tokens: list of stemmed query tokens
:param postings: dictionary of terms and their positions for each doc,
assumes a list has alr been obtained for all query tokens

:return result: list of docs containing the phrase
"""
def phrasal_query(query_tokens, postings):
    """
    postings:
    {
        Term1: {
            Node1 containing [position1, position2, ...]
            Node2 containing [position1, position2, ...]
        }
        ...
    }

    2-way merge: take first 2 terms to look through positions first, then add another
    """

    simplified_posting = {}
    # only store { token: { docID: [positions] } }
    for token in query_tokens:
        if token not in simplified_posting:
            simplified_posting[token] = {}

        docs = simplified_posting[token]

        for node in postings[token]:
            docID = node.get_doc_id() # should only encounter each docID once
            docs[docID] = node.get_positions()

    # adding the docs and corresponding positions for all query tokens
    # needs to be refreshed for every new query
    phrase_postings = []

    for token in query_tokens:
        if token in simplified_posting:
            phrase_postings.append(simplified_posting[token]) # returns a dictionary of { docID : positions }
            # words not in dictionary are ignored

    if phrase_postings:
        result = phrase_postings[0] # in case there's only one word in the phrase that is in the dict

        # compare 2-way at a time, only need to compare w the token before
        for i in range (1, len(phrase_postings)): # TODO assuming for now a normal case only
            token1_docs = result
            token2_docs = phrase_postings[i]

            # find intersection of docIDs
            shared_docs = set(token1_docs.keys()).intersection(set(token2_docs.keys()))

            temp = {} # after looking through docs containing the exact phrase

            for doc in shared_docs:
                p1 = token1_docs[doc]
                p2 = token2_docs[doc]

                temp[doc] = get_consecutives(p1, p2) # can be empty list, but maintain same format for future merging

            result = temp

        return result # dictionary of docs with a list of the positions of the last query token, after making sure the
                      # positions of the other words are correct

    else: # if no token in phrase is in dictionary
        return []

"""
posting = {
    "term1": {
        1: [1, 2, 4, 5],
        2: [2, 6, 9]
    },

    "term2": {
        1: [1, 3, 6],
        2: [1, 6, 10]
    }
}
"""

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
    Same as homework 3 - to be improved upon (atharv)
    """
    with open(queries_file, 'r') as query_file:
        query_content = query_file.read().splitlines()
        query = query_content.pop(0) # first line in query file is the query
        relevance_judgements = query_content # remaining entries in query_content are the given relevance judgements

    # parse and evaluate each query and write results to disk one by one
    with open(queries_file, 'r') as q, open(results_file, 'w') as r:
        queries = q.read().splitlines()

        for query in queries:
            print("processing " + query + "...")
            parsed_query = parse_query(query)
            results = evaluate_query(parsed_query, dictionary, postings)
            result_string = " ".join(str(i) for i in results)
            r.write(result_string + '\n')

dictionary_file = postings_file = file_of_queries = output_file_of_results = None

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
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or output_file_of_results == None :
    usage()
    sys.exit(2)

start_time = time.time()  # clock the run
run_search(dictionary_file, postings_file, file_of_queries, output_file_of_results)
end_time = time.time()
print('search completed in ' + str(round(end_time - start_time, 2)) + 's')
