from collections import defaultdict
from nltk.stem import PorterStemmer
import math
import pickle

stemmer = PorterStemmer()

"""
Rank phrasal search by tf (log) of the entire phrase.

:param intermediate_result: a dictionary of {docID: [positions]}, passed from phrasal_search
:param doc_lengths: a dictionary of { docID: doc_length }, to normalise
"""
def rank_phrasal_by_tf(intermediate_result, doc_lengths):
    doc_to_tf = {} # docID: normalised tf
    for docID in intermediate_result:
        doc_to_tf[docID] = len(intermediate_result[docID]) / doc_lengths[docID] # tf / doc_length, normalisation

    ranked = sorted(doc_to_tf.items(), key=lambda x: x[1], reverse=True) # sorted in desc order by normalised tf
    return [x[0] for x in ranked] # return only docID


"""
Ranking by tf of the query taken as free text.

:param query_tokens: list of stemmed query tokens
:param relevant_docIDs: a list of relevant docIDs for the query
:param dictionary: { token: (df, pointer) }
:param postings_file: the file containing postings written in disk
:param doc_lengths: a dictionary of { docID: doc_length }, to normalise
"""
def rank_boolean_by_tf(query_tokens, relevant_docIDs, dictionary, postings_file, doc_lengths):
    filtered_postings = {} # { token: { docID: tf } } --> { token: sorted(docID, tf) }
    scores = {} # { docID: total_tf_for_all_query_tokens }

    # get postings for all query tokens first
    temp = get_postings(query_tokens, dictionary, postings_file)


    # rank by cosine scoring!!!!!!!


    for token in query_tokens:
        docs = temp[token]
        for docID in docs:
            if docID in relevant_docIDs:
                tf = len(temp[docID]) # no. of occurrences = frequency

                if token not in filtered_postings:
                    filtered_postings[token] = {docID: tf} # tf(token) = len(positions)
                else:
                    filtered_postings[token][docID] = tf # each token only encounters each docID once

                if docID not in scores:
                    scores[docID] = tf
                else:
                    scores[docID] += tf

    # normalise by doc_lengths
    for docID in scores:
        tf = scores[docID]
        assert(tf > 0)

        scores[docID] = tf / doc_lengths[docID]

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)  # sort scores by descending order

    results = [entry[0] for entry in sorted_scores]
    return results

# """
# :param node: contains docID, positional indices, next node, skip node
# fields and corresponding boolean values
#
# :param zone_weights: weights given to each zone to be multiplied with boolean
# :return zone_score: sum of zone_score for each zone
# """
# def get_weighted_zone(node, zone_weights):
#     """
#     implementation 1: every zone contains a boolean value
#
#     implementation 2: node has attributes "in_metadata" and "in_body",
#     with boolean values for both, so calculation is only done based on these two.
#     """
#     # assuming implementation 2
#
#     return node.in_metadata * zone_weights[0] + node.in_body * zone_weights[1]

# METHODS FOR PARSING AND EVALUATING QUERY #

def parse_query(query):
    """
    Parses the query and returns a list of lists corresponding to the parsed query.

    The number of items in the outer list correspond to the number of queries separated by AND. The inner list either
    contains a parsed phrase corresponding to a phrasal query or is a list of tokens corresponding to a free text query.
    Multi-word free text queries in an AND query are treated as AND queries on each word.

    :param query the query to be parsed
    :return a list of lists corresponding to the parsed query, or an empty list if query is an empty string
    """
    # delimit query by AND
    split_query = [subquery.strip() for subquery in query.split("AND")]

    parsed_query = []

    # for-loop appends a parsed subquery list for every subquery encountered,
    # and since subqueries are produced by delimiting with "AND",
    # only boolean queries will have multiple subqueries.
    for subquery in split_query:
        # ignores for empty query
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

    :param query the multiword free text query to be parsed
    :return a list containing individual parsed tokens from the multiword query
    """
    tokens = query.split(" ") # split query into individual words
    stemmed_tokens = [stemmer.stem(token.lower()) for token in tokens]
    return stemmed_tokens

def parse_phrasal_query(query):
    """
    Parse phrasal query by tokenizing, stemming, rejoining and striping off quotation marks

    :param query the phrasal query to be parsed
    :return a list containing the parsed phrasal query
    """
    query = query.strip('"') # remove quotation marks
    tokens = query.split(" ") # split query into individual words
    stemmed_tokens = [stemmer.stem(token.lower()) for token in tokens]
    parsed_phrasal_query = " ".join(str(i) for i in stemmed_tokens)
    return [parsed_phrasal_query]

"""
Evaluate a parsed query by calling the appropriate search functions.

If the parsed query list has more than one item, call boolean AND search. If the parsed query list has one item,
and if the item is a phrase, call phrasal search. Else, call vector space model search. One-word phrasal queries are
treated as one-word free text queries and searched using VSM.

:param query a list of lists corresponding to the parsed query to be evaluated
:param dictionary the dictionary of Terms saved to disk
:param doc_lengths the dictionary of document lengths with doc_id as key and document length as value
:param postings_file the file containing postings written in disk

:return a list of relevant documents depending on the query
"""
def evaluate_query(query, dictionary, doc_lengths, postings_file):
    # check for empty query
    if not query:
        return []
    # check for boolean query
    elif (len(query) > 1):
        # flatten the list of lists into a list of independent queries to be supplied to the boolean AND search function
        flattened_query = [subquery for inner_list in query for subquery in inner_list]

        # call boolean search, which will obtain the postings as required
        results = boolean_search(flattened_query, dictionary, postings_file, doc_lengths)
        # TODO rank results from boolean search using VSM search on query
        return results

    else: # no AND, either phrasal query or free text query
        # this should be true as non-boolean searches should only have 1 subquery.
        assert(len(query) == 1)

        # check for phrasal query by checking if there is a space in the first subquery
        first_subquery = query[0][0]
        if " " in first_subquery:
            # obtain individual tokens in phrasal query
            tokenised_phrasal_query = first_subquery.split(" ")

            # call phrasal search, which will obtain the postings as required
            # this phrasal search is not embedded in a boolean search, thus is_boolean = False
            results = phrasal_search(tokenised_phrasal_query, dictionary, postings_file, doc_lengths, False)
            return results

        else: # free text query, run VSM search
            tokenised_free_text_query = query[0]

            # call VSM search, which will obtain the postings as required
            results = VSM_search(tokenised_free_text_query, dictionary, postings_file, doc_lengths)
            return results

def get_postings(query, dictionary, postings_file):
    """
    Returns postings of each token in the given query.

    :param query: a list containing query tokens
    :param dictionary the dictionary of terms saved to disk
    :param postings_file the file containing postings written in disk
    :return a dictionary of dictionaries containing postings information. The outer dictionary has token as key and
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

# METHODS FOR VSM SEARCH FOR FREE TEXT QUERIES #

"""
:param query: list of stemmed query tokens
:param dictionary: { token: (df, pointer) }
:param postings_file: postings.txt
:param doc_lengths: a dictionary of { docID: doc_length }
"""
def VSM_search(query, dictionary, postings_file, doc_lengths):
    # get postings for each token in query if that token exists in dictionary
    postings = get_postings(query, dictionary, postings_file)

    # build query_vector with key: token, value: normalised w_tq of token
    N = len(doc_lengths) # N is the total number of documents in the corpus
    query_vector = build_query_vector(query, dictionary, N)

    # calculate scores with key: docID, value: cosine score of document corresponding to docID
    scores = calculate_cosine_scores(query_vector, postings, doc_lengths)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)  # sort scores by descending order

    # TODO determine threshold cosine score for relevance, currently set to 0
    threshold_score = 0
    results = [entry[0] for entry in sorted_scores if entry[1] > threshold_score]
    return results

def build_query_vector(query, dictionary, N):
    """
    Return normalised tf-idf score for given query in ltc scheme.

    :param query the query from which query vector is to be built
    :param dictionary the dictionary of terms saved to disk
    :param N the number of documents in the corpus
    :return query vector containing dictionary token as key and normalised w_tq of token as value
    """
    query_vector = defaultdict(float) # key: token, value: normalised w_tq of token

    # calculate token frequency
    for token in query:
        query_vector[token] += 1

    # calculate weighted token frequency for each token
    for token in query_vector:
        # get df
        df = dictionary[token][0] if token in dictionary else 0

        # calculate idf
        idf = 0.0 if (df == 0) else math.log((N / df), 10)

        # calculate logarithmic token frequency
        tf = query_vector[token]
        ltf = 1 + math.log(tf, 10)

        # calculate and store weighted token frequency
        w_tq = ltf * idf
        query_vector[token] = w_tq

    # query length not calculated as it does not affect ranking of final results
    return query_vector

def calculate_cosine_scores(query_vector, postings, doc_lengths):
    """
    Return normalised tf-idf score for given query in ltc scheme in the form of a dictionary.
    :return dictionary containing document IDs as key and cosine scores as values
    """
    scores = {} # key: docID, value: cosine score
    for token in postings:
        for doc_id in postings[token]:
            # calculate weighted token frequency
            tf = len(postings[token][doc_id])
            ltf = 1 + math.log(tf, 10)

            # update scores
            if doc_id in scores:
                scores[doc_id] += ltf * query_vector[token]
            else:
                scores[doc_id] = ltf * query_vector[token]

    # normalise all scores by dividing by document length
    for doc_id, score in scores.items():
        doc_length = doc_lengths[doc_id]
        scores[doc_id] = score / doc_length

    return scores

# METHODS FOR BOOLEAN 'AND' SEARCH FOR BOOLEAN QUERIES #

"""
Finds intersection of two iterables of docIDs, sorted in asc order

:param lst1: iterable of token1
:param lst2: iterable of token2

:return: list of common docIDs
"""

def and_merge(lst1, lst2):
    return sorted(list(set(lst1).intersection(set(lst2))))

"""
Runs boolean search by calling AND merge function on each subquery.

:param query: list of stemmed subquery tokens, phrasal searches given as a phrase without quotation but with space
:param dictionary: { token: (df, pointer) }
:param postings_file: postings.txt
:return result: list of docIDs
"""
def boolean_search(query, dictionary, postings_file, doc_lengths):
    results = [] # container for results of list intersection
    for i in range(len(query)):
        subquery = query[i]

        # check if subquery is a phrase
        if " " in subquery:
            # run phrasal search after splitting phrasal subquery, returns a list of relevant doc_ids
            tokenised_phrasal_query = subquery.split(" ")
            # this phrasal search is embedded in a boolean search, thus is_boolean = True
            temp_results = phrasal_search(tokenised_phrasal_query, dictionary, postings_file, doc_lengths, True)

        else:
            # a single word
            postings = get_postings([subquery], dictionary, postings_file)

            if subquery not in dictionary:
                return []

            temp_results = postings[subquery]

        # merge two lists only if subquery is not the first subquery in query
        if (i != 0):
            assert (results) # results must not be empty
            results = and_merge(results, temp_results)
        else:
            results = temp_results

    # rank results
    ranked_results = rank_boolean_by_tf(query, results, dictionary, postings_file, doc_lengths)

    return ranked_results # ranked list of docIDs

# METHODS FOR PHRASAL SEARCH FOR PHRASAL QUERIES #

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
            # only store the position of the last word of the phrase
            # to facilitate recursive get_consecutive.
            # the length of the final list will be the tf of the phrase.
            result.append(p2)

            i += 1
            j += 1

        else:
            i += 1

    return result

"""
Takes a phrase and does two-way checking of positions at a time.
Handles the case where there is only 1 word in phrase.

:param tokenised_phrasal_query: list of stemmed query tokens
:param dictionary: { token: (df, pointer) }
:param postings_file: postings.txt
:param is_boolean: whether the phrase was passed from a boolean search, used for RANKING phrasal searches...

:return result: list of docIDs
"""
def phrasal_search(tokenised_phrasal_query, dictionary, postings_file, doc_lengths, is_boolean):
    results = {} # key - doc_id, value - list of positions in document of the last word in phrase

    # retrieve postings of each token in phrasal query
    # postings may be empty, if none of the query tokens are in dictionary
    postings = get_postings(tokenised_phrasal_query, dictionary, postings_file)

    # compare 2-way at a time, that is, compare this token with the preceding token
    for i in range(len(tokenised_phrasal_query)):
        token = tokenised_phrasal_query[i]

        if token not in dictionary:
            return []

        token_postings = postings[token] # get { docID: [positions] }

        # continue loop if token is the first token in phrase after setting temp_results to postings of first token
        if (i == 0):
            results = token_postings
        else:
            assert (results) # results must not be empty
            # token is not first token, continue with phrasal search
            # find intersection of docIDs as a list
            shared_docs = and_merge(results.keys(), token_postings.keys())

            intermediate_results = {}  # container to hold intermediate results of positional intersect
            for doc_id in shared_docs:
                p1 = results[doc_id]  # list of positions of last word in previous iteration
                p2 = token_postings[doc_id]  # positions of current token

                intermediate_results[doc_id] = get_consecutives(p1, p2)

            results = intermediate_results

    if not is_boolean:
        return rank_phrasal_by_tf(results, doc_lengths)

    return list(results.keys())
