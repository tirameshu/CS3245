#!/usr/bin/python3
from __future__ import division

import math
import re
import sys
import getopt
import pickle

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer

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
def get_all_relevant_lists(query_terms, dictionary, postings, relevant_postings, score_calc):
    processed_query_terms = list(map(lambda x: process_query_term(x), query_terms))

    for term in processed_query_terms:
        if term in dictionary:
            if term not in relevant_postings:
                df, postings_pointer = dictionary[term]

                postings.seek(postings_pointer)
                all_postings = pickle.load(postings) # alr in desc order

                # champions.seek(champion_pointer)
                # champion_list = pickle.load(champions)

                assert isinstance(all_postings, list)
                relevant_postings[term] = all_postings
                assert isinstance(all_postings[0], tuple)

                score_calc[term] = 0 # only for terms in both query n dict, for convenience

                dictionary[term].append(1)
            else:
                df, pointer_to_posting, tf_q = dictionary[term]
                tf_q += 1
                dictionary[term] = [df, pointer_to_posting, tf_q]

def find_q_length_from_w_tq(dictionary, relevant_postings, score_calc, docLengths):
    N = len(docLengths)
    pre_length_sum = 0
    for term in score_calc:
        df, postings_pointer, tf_q = dictionary[term]
        weighted_tf_q = 1 + math.log(tf_q, 10)

        idf = math.log(N / df)
        w_tq = weighted_tf_q * idf

        pre_length_sum += w_tq

        for posting in relevant_postings[term]:
            docID, norm_w = posting # norm_w = w_td / docL

            if term not in score_calc:
                score_calc[term] = {docID: [w_tq, norm_w]}
            else:
                score_calc[term][docID] = [w_tq, norm_w]

    if pre_length_sum:
        q_length = math.sqrt(pre_length_sum)
        return q_length
    else:
        print("q_length cannot be 0!")
        return 0

def normalise_and_score(score_calc, q_length, scores):
    for term in score_calc:
        docs = score_calc[term]
        for docID in docs:
            w_tq, norm_w = docs[docID]
            norm_w_tq = w_tq / q_length
            score = norm_w * norm_w_tq

            if docID not in scores:
                scores[docID] = score
            else:
                scores[docID] += score

def rank_and_get_top_docs(scores):
    # for now get top 3 first
    scores = scores.items()
    scores.sort(key=lambda x: x[1], reverse=True) # desc order

    ranked_scores = list(set(map(lambda x: x[1], scores))) # set of all scores
    ranked_scores.sort(reverse=True) # rank them
    top_docs = []
    for score in ranked_scores:
        if score[1] < ranked_scores[max(len(ranked_scores), 2)]: # TODO: change to 9 eventually
            break
        else:
            top_docs.append(score)

    return top_docs


def run_search(dict_file, postings_file, queries_file, results_file):
    print('running search on the queries...')

    dict = open(dict_file, "rb")
    postings = open(postings_file, "rb")
    # champions = open("champion_list.txt", "rb")
    queries = open(queries_file, "r")
    results = open(results_file, "a+")

    docLengths = pickle.load(dict)
    dictionary = pickle.load(dict)

    """
    dictionary:
    {term1: [df, pointer_to_posting, tf_q] # tf_q = term count in query
    ...
    }
    """

    relevant_postings = {}

    for query_line in queries:
        score_calc = {} # reset for every query
        scores = {}
        sentence = sent_tokenize(query_line)
        query_terms = word_tokenize(sentence[0])

        get_all_relevant_lists(query_terms, dictionary, postings, relevant_postings, score_calc)

        q_length = find_q_length_from_w_tq(dictionary, relevant_postings, score_calc, docLengths)

        normalise_and_score(score_calc, q_length, scores)

        top_docs = rank_and_get_top_docs(scores)

        if top_docs:
            results.write(" ".join(map(lambda x: str(x[0]), top_docs)) + "\n")
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
