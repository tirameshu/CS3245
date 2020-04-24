import re
import sys
import getopt
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import time
import math
import pickle

def parse_query(query):
    """
    Parses the query and returns a list of lists corresponding to the parsed query.

    The number of items in the outer list correspond to the number of queries separated by AND. The inner list either
    contains a parsed phrase corresponding to a phrasal query or is a list of tokens corresponding to a free text query.
    Multi-word free text queries in an AND query are treated as AND queries on each word.

    @param query the query to be parsed
    @return a list of lists corresponding to the parsed query, or an empty list if query is an empty string
    """
    # delimit query by AND
    split_query = [subquery.strip() for subquery in query.split("AND")]

    parsed_query = []

    for subquery in split_query:
        # check for empty query
        if not subquery:
            continue

        # check for phrasal query
        if subquery[0] == "\"":
            parsed_phrasal_query = parse_phrasal_query(subquery) # returns a list
            parsed_query.append(parsed_phrasal_query)
        else: # subquery is either single word free text query or multi-word free text query
            if " " in subquery: # true for multi-word queries
                parsed_multiword_free_text_query = parse_multiword_free_text_query(subquery) # returns a list
                parsed_query.append(parsed_multiword_free_text_query)

            else:
                parsed_query.append([stemmer.stem(subquery.lower())])

    return parsed_query

def parse_multiword_free_text_query(query):
    """
    Parses multiword free text query by tokenising, stemming, and case folding

    @param query the multiword free text query to be parsed
    @return a list containing individual parsed tokens from the multiword query
    """
    tokens = query.split(" ") # split query into individual words
    stemmed_tokens = [stemmer.stem(token.lower()) for token in tokens]
    return stemmed_tokens

def parse_phrasal_query(query):
    """
    Parse phrasal query by tokenizing, stemming, rejoining and striping off quotation marks

    @param query the phrasal query to be parsed
    @return a list containing the parsed phrasal query
    """
    query = query.strip('"') # remove quotation marks
    tokens = query.split(" ") # split query into individual words
    stemmed_tokens = [stemmer.stem(token.lower()) for token in tokens]
    parsed_phrasal_query = " ".join(str(i) for i in stemmed_tokens)
    return [parsed_phrasal_query]

def evaluate_query(query, dictionary, doc_lengths, postings_file):
    """
    Evaluate a parsed query by calling the appropriate search functions.

    If the parsed query list has more than one item, call boolean AND search. If the parsed query list has one item,
    and if the item is a phrase, call phrasal search. Else, call vector space model search.

    @param query a list of lists corresponding to the parsed query to be evaluated
    @param dictionary the dictionary of Terms saved to disk
    @param doc_lengths the dictionary of document lengths with doc_id as key and document length as value
    @param postings_file the file containing postings written in disk
    @return a list of relevant documents depending on the query
    """
    # check for empty query
    if not query:
        return []
    # check for boolean query
    elif (len(query) > 1):
        # flatten the list of lists into a list of independent queries to be supplied to the boolean AND search function
        flattened_query = [subquery for inner_list in query for subquery in inner_list]

        # call boolean search, which will obtain the postings as required
        results = boolean_search(flattened_query, dictionary, postings_file)
        # TODO rank results from boolean search using VSM search on query
        return results

    else: # no AND, either phrasal query or free text query
        # check for phrasal query
        if " " in query[0]:
            # obtain individual tokens in phrasal query
            tokenised_phrasal_query = query[0].split(" ")

            # call phrasal search, which will obtain the postings as required
            results = phrasal_search(tokenised_phrasal_query, dictionary, postings_file)
            return results

        else: # free text query, run VSM search
            tokenised_free_text_query = query[0]

            # call VSM search, which will obtain the postings as required
            results = VSM_search(tokenised_free_text_query, dictionary, postings_file, doc_lengths)
            return results

def get_postings(query, dictionary, postings_file):
    """
    Returns postings of each token in the given query

    @param query a list containing query tokens
    @param dictionary the dictionary of Terms saved to disk
    @param postings_file the file containing postings written in disk
    @return a dictionary of dictionaries containing postings information. The outer dictionary has token as key and
    value of an inner dictionary with doc_id as key and list of positional indices as value.
    """
    postings = {}

    with open(postings_file, 'rb') as post:
        for token in query:
            if token in dictionary:
                pointer = dictionary[token][1]
                post.seek(pointer)
                postings_list = pickle.load(post)  # obtain postings list corresponding to term
                postings[token] = postings_list
                post.seek(0)  # rewind

    return postings

def VSM_search(query, dictionary, postings_file, doc_lengths):
    # build query_vector with key: token, value: normalised w_tq of token
    query_vector = build_query_vector(query[0], dictionary)

    # calculate scores with key: docID, value: cosine score of document corresponding to docID
    scores = calculate_cosine_scores(query[0], query_vector, dictionary, postings_file, doc_lengths)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)  # sort scores by descending order

    # TODO determine threshold cosine score for relevance, currently set to 0
    threshold_score = 0
    results = [entry[0] for entry in sorted_scores if entry[1] > threshold_score]
    return results

def build_query_vector(query, dictionary):
    """
    Return normalised tf-idf score for given query in ltc scheme in the form of a dictionary.
    @return query vector containing dictionary token as key and normalised w_tq of token as value
    """
    query_vector = {} # key: token, value: normalised w_tq of token

    # calculate token frequency
    for token in query:
        if token in query_vector:
            query_vector[token] += 1
        else:
            query_vector[token] = 1

    # calculate weighted token frequency
    N = dictionary.get_no_of_docs() # N is the total number of documents in the corpus
    w_tq_running_total = 0  # for calculating query length
    for token in query_vector:
        # get df
        df = dictionary.get_df(token)

        # calculate idf
        idf = 0 if (df == 0) else math.log((N / df), 10)

        # calculate logarithmic token frequency
        tf = query_vector[token]
        ltf = 1 + math.log(tf, 10)

        # calculate and store weighted token frequency
        w_tq = ltf * idf
        query_vector[token] = w_tq

        # update w_tq running total for calculating query length
        w_tq_running_total += w_tq ** 2

    # calculate normalised weighted token frequency
    query_length = math.sqrt(w_tq_running_total)
    for token in query_vector:
        if query_length: # check for zero query length
            query_vector[token] /= query_length
        else:
            query_vector[token] = 0

    return query_vector

def calculate_cosine_scores(query, query_vector, dictionary, postings_file, doc_lengths):
    """
    Return normalised tf-idf score for given query in ltc scheme in the form of a dictionary.
    @return dictionary containing document IDs as key and cosine scores as values
    """
    scores = {} # key: docID, value: cosine score

    postings = get_postings(query, dictionary, postings_file)

            for posting in postings_list:
                docID = posting[0]

                # calculate weighted token frequency
                tf = posting[1]
                ltf = 1 + math.log(tf, 10)

                # update scores
                if docID in scores:
                    scores[docID] += ltf * query_vector[token]
                else:
                    scores[docID] = ltf * query_vector[token]

    # normalise all scores by dividing by document length
    for docID, score in scores.items():
        doc_length = dictionary.get_doc_length(docID)
        scores[docID] = score / doc_length

    return scores

stemmer = PorterStemmer()
