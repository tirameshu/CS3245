#!/usr/bin/python3
import re
import sys
import getopt
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import time
import math
import pickle
import heapq

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def parse_query(query):
    """
    Returns a list of word tokens from the input query after stemming and case folding. Only alphanumerical terms in the
    input query are considered.

    @param query string representing the query to be processed
    @return list of tokens from the input query after processing
    """
    return [PorterStemmer().stem(token.lower()) for token in word_tokenize(query) if token.isalnum()]

def evaluate(query, dict_file, postings_file):
    """
    Evaluate a parsed query by building query vector and calculating cosine scores to return the doc IDs of the top ten
    most relevant documents.

    @param query list containing tokens of the parsed query
    @param dict_file input file containing the dictionary stored in the disk
    @param postings_file input file containing the postings lists stored in the disk
    @return list containing doc IDs of the top 10 most relevant documents
    """
    with open(dict_file, 'rb') as d:
        # retrieve document lengths and vocabulary
        doc_lengths = pickle.load(d)
        dictionary = pickle.load(d)

        N = len(doc_lengths) # N is the total number of documents in corpus

        # build query_vector with key: term, value: normalised w_tq of term
        query_vector = build_query_vector(query, dictionary, N)

        # calculate scores with key: docID, value: cosine score of document corresponding to docID
        scores = calculate_cosine_scores(query_vector, dictionary, doc_lengths, postings_file)

        # return top ten highest scores as a list
        top_scores = heapq.nlargest(min(len(scores), no_of_results), scores.items(), key=lambda i: i[1])
        top_docs = [score[0] for score in top_scores]

    return top_docs

def build_query_vector(query, dictionary, N):
    """
    Return normalised tf-idf score for given query in ltc scheme in the form of a dictionary.

    @param query list containing tokens of the parsed query
    @param dictionary a dictionary containing the vocabulary, document frequency, and pointer to postings list
    @param N integer representing the total number of documents in the corpus
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
    w_tq_running_total = 0  # for calculating query length
    for term in query_vector:
        # get df
        df = dictionary[term][0] if term in dictionary else 0

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

def calculate_cosine_scores(query_vector, dictionary, doc_lengths, postings_file):
    """
    Return normalised tf-idf score for given query in ltc scheme in the form of a dictionary.

    @param query_vector dictionary representing the query vector
    @param dictionary dictionary a dictionary containing the vocabulary, document frequency, and pointer to postings list
    @param doc_lengths list of document lengths for all documents in the corpus
    @param postings_file input file containing the postings lists stored in the disk
    @return dictionary containing document IDs as key and cosine scores as values
    """
    scores = {} # key: docID, value: cosine score
    with open(postings_file, 'rb') as p:
        for term in query_vector:
            if term in dictionary:
                pointer = dictionary[term][1]
                p.seek(pointer)
                postings_list = pickle.load(p) # obtain postings list corresponding to term
                p.seek(0) # rewind

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
        doc_length = doc_lengths[docID]
        scores[docID] = score / doc_length

    return scores

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file, perform searching on the given queries file and output the
    results to a file.

    @dict_file input file containing the dictionary stored in the disk
    @postings_file input file containing the postings lists stored in the disk
    @param queries_file input file with each line containing a query to be processed
    @param results_file output file to write the results of the search to
    """
    print('running search on the queries...')
    start_time = time.time() # clock the run

    # parse and evaluate each query and write results to disk one by one
    with open(queries_file, 'r') as q, open(results_file, 'w') as r:
        queries = q.read().splitlines()
        for query in queries:
            print("processing " + query + "...")
            parsed_query = parse_query(query)
            results = evaluate(parsed_query, dict_file, postings_file)
            result_string = " ".join(str(i) for i in results)
            r.write(result_string + '\n')

    end_time = time.time()
    print('search completed in ' + str(round(end_time - start_time, 2)) + 's')

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

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

no_of_results = 10 # return only top 10 results
run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
