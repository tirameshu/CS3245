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

def parse_query(query):
    """
    Returns a list of word tokens from the input query after stemming and case folding.
    """
    return [PorterStemmer().stem(token.lower()) for token in word_tokenize(query)]

def evaluate_query(query, dictionary, postings):
    """
    Evaluate a parsed query by building query vector and calculating cosine scores to return the doc IDs of the top ten
    most relevant documents.
    """
    # retrieve document lengths and vocabulary
    dictionary.load()

    # build query_vector with key: term, value: normalised w_tq of term
    query_vector = build_query_vector(query, dictionary)

    # calculate scores with key: docID, value: cosine score of document corresponding to docID
    scores = calculate_cosine_scores(query_vector, dictionary, postings)

    # return top ten highest scores as a list
    top_scores = heapq.nlargest(min(len(scores), no_of_results), scores.items(), key=lambda i: i[1])
    top_docs = [score[0] for score in top_scores]

    return top_docs

def build_query_vector(query, dictionary):
    """
    Return normalised tf-idf score for given query in ltc scheme in the form of a dictionary.
    @return query vector containing dictionary term as key and normalised w_tq of term as value
    """
    query_vector = {} # key: term, value: normalised w_tq of term

    # calculate term frequency
    for term in query:
        if term in query_vector:
            query_vector[term] += 1
        else:
            query_vector[term] = 1

    # calculate weighted term frequency
    N = dictionary.get_no_of_docs() # N is the total number of documents in the corpus
    w_tq_running_total = 0  # for calculating query length
    for term in query_vector:
        # get df
        df = dictionary.get_df(term)

        # calculate idf
        idf = 0 if (df == 0) else math.log((N / df), 10)

        # calculate logarithmic term frequency
        tf = query_vector[term]
        ltf = 1 + math.log(tf, 10)

        # calculate and store weighted term frequency
        w_tq = ltf * idf
        query_vector[term] = w_tq

        # update w_tq running total for calculating query length
        w_tq_running_total += w_tq ** 2

    # calculate normalised weighted term frequency
    query_length = math.sqrt(w_tq_running_total)
    for term in query_vector:
        if query_length: # check for zero query length
            query_vector[term] /= query_length
        else:
            query_vector[term] = 0

    return query_vector

def calculate_cosine_scores(query_vector, dictionary, postings):
    """
    Return normalised tf-idf score for given query in ltc scheme in the form of a dictionary.
    @return dictionary containing document IDs as key and cosine scores as values
    """
    scores = {} # key: docID, value: cosine score

    for term in query_vector:
        if dictionary.has_term(term):
            pointer = dictionary.get_pointer(term)
            postings_list = postings.load(pointer)

            for posting in postings_list:
                docID = posting[0]

                # calculate weighted term frequency
                tf = posting[1]
                ltf = 1 + math.log(tf, 10)

                # update scores
                if docID in scores:
                    scores[docID] += ltf * query_vector[term]
                else:
                    scores[docID] = ltf * query_vector[term]

    # normalise all scores by dividing by document length
    for docID, score in scores.items():
        doc_length = dictionary.get_doc_length(docID)
        scores[docID] = score / doc_length

    return scores

no_of_results = 10 # return only top 10 results
