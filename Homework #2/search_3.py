#!/usr/bin/python3
import math
import re
import sys
import getopt
import pickle

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer

score = {}

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

"""
Dictionary contains no symbols; situations like "hi!" is tokenized into "hi", "!"
So queries containing non-alpha chars will render no results anyway, similar to searching for empty string
"""
def process_query_term(query_term):
    ps = PorterStemmer()
    if query_term.isalpha():
        term = query_term.strip()
        term = ps.stem(term)
        return term.lower()
    return ""

"""
Gets postings list for all terms queried
Checks whether term has already been queried --> don't update existing terms for subsequent queries
If queried term is not in dictionary, it is ignored as it does not affect the score
"""
def get_all_relevant_lists(query_terms, dictionary, postings, relevant_postings):
    processed_query_terms = list(map(lambda x: process_query_term(x), query_terms))

    for term in processed_query_terms:
        if term not in relevant_postings and term in dictionary:
            df, postings_pointer = dictionary[term]

            postings.seek(postings_pointer)
            all_postings = pickle.load(postings)

            # champions.seek(champion_pointer)
            # champion_list = pickle.load(champions)

            docs.sort(key=lambda x: x.docID) # sort from the start

            assert isinstance(docs, list)
            dictionary[term] = docs

"""
Just to flatten and remove brackets
() > NOT > AND > OR 
"""
def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    dict = open(dict_file, "rb")
    postings = open(postings_file, "rb")
    # champions = open("champion_list.txt", "rb")
    queries = open(queries_file, "r")
    results = open(results_file, "a+")

    docLengths = pickle.load(dict)
    dictionary = pickle.load(dict)

    relevant_postings = {}

    """
    Assumes that query individual words joined by logic operators, ie no bill gates AND vista
    Does NOT assume that only logic operators are all uppercase
    """
    for query_line in queries:
        sentence = sent_tokenize(query_line)
        query_terms = word_tokenize(sentence[0])

        get_all_relevant_lists(query_terms, dictionary, postings, relevant_postings)

        if len(query_terms) == 1: # non-logical searches
            result = indiv_search(query_terms[0])
        else:
            for query_term in query_terms:
                # print("run_search:")
                # print(stack)
                # brackets take priority
                if query_term == ")":
                    term = stack.pop()
                    while term != "(": # process bracketed exp first
                        to_merge.insert(0, term)
                        term = stack.pop()
                    # print("line 210: to merge ")
                    # print(to_merge)

                    """
                    merging!
                    """
                    result = simple_merge(to_merge, dict)  # list of docIDs
                    stack.append(result)  # stack can become nested list
                else:
                    stack.append(query_term)
            # by the end of this loop, the stack should just be
            # A AND NOT B OR C[] kind of thing

            # print("end of run_search loop, stack:")
            # print(stack)

            """
            merging!
            """
            result = simple_merge(stack, dict)

        if result:
            # if type(result) == str:
                # print("result is string: " + result)
            result.sort(key=lambda x: x.docID)
            results.write(" ".join(map(lambda x: str(x.docID), result)) + "\n")
        else:
            results.write("\n")

    dict.close()
    postings.close()
    queries.close()
    results.close()


dictionary_file = postings_file = file_of_queries = file_of_output = None

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

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
