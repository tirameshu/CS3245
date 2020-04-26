from collections import defaultdict
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.stem import PorterStemmer
from numpy import mean, quantile

import math
import nltk
import pickle


stemmer = PorterStemmer()
stop_words = set(stopwords.words('english')) # set stop words to those of English language
no_of_quantiles = 100  # for determining threshold for cosine scoring - by default, use percentiles

def get_courts():
    most_impt_courts = []
    less_impt_courts = []

    with open("Notes about Court Hierarchy.txt", 'r') as court_hierarchy:
        most_impt_flag = False
        less_impt_flag = False
        for line in court_hierarchy:
            line = line.strip()
            if line == "The rest":
                break
            elif line == "Most important":
                most_impt_flag = True
                continue
            elif line == "?Important?":
                less_impt_flag = True
                continue

            if most_impt_flag:
                if not line.strip():  # empty line, end of most impt courts
                    most_impt_flag = False
                else:  # still in most impt courts
                    most_impt_courts.append(line.strip())

            if less_impt_flag:
                if not line.strip():  # empty line, end of most impt courts
                    less_impt_flag = False
                else:  # still in most impt courts
                    less_impt_courts.append(line.strip())

    return most_impt_courts, less_impt_courts

"""
Sorts docIDs by whether any part of the query is in their title.

:param results: a list of docIDs
:param first: first metadata field to sort by
:param second: as above
:param third: as above

:return sorted docIDs according to param sequence.
"""
def sort_results_by_metadata(results, metadata, query_tokens):
    most_impt_courts, less_impt_courts = get_courts()

    doc_with_metadata = {} # Python3.7 onwards this preserves insertion order

    sorted_by_metadata = []

    i = 0
    for docID in results:
        if docID not in doc_with_metadata: # prevents duplicate results
            if i < 100: # only sort for the first 100 docs
                title, year, court = metadata[docID]
                query_in_title = 0
                court_score = 0

                # if title contains query, give it a 1 and later sort in reverse order
                for token in query_tokens:
                    if token in title:
                        # there are mostly no stopwords in free text query,
                        # and for phrasal search we assume all words matter,
                        # and for boolean searches, if stopwords exist, they
                        query_in_title = +1

                # if court is most impt, give score 2; less impt give score 1, others 0
                if court in most_impt_courts:
                    court_score = 2
                elif court in less_impt_courts:
                    court_score = 1

                doc_with_metadata[docID] = [query_in_title, year, court_score]
            elif i >= 100:
                sorted_by_metadata.append(docID)

            if i == 99: # 100th doc has been processed and added into doc_with_metadata
                doc_with_metadata = list(doc_with_metadata.items()) # for 100 docs
                print("doc_with_metadata:")
                print(doc_with_metadata[:20])

                doc_with_metadata.sort(key=lambda x: x[1][0], reverse=True) # first by title
                doc_with_metadata.sort(key=lambda x: x[1][1], reverse=True) # then by year
                doc_with_metadata.sort(key=lambda x: x[1][2], reverse=True) # then by court

                first_100_sorted_by_metadata = list(map(lambda x: x[0], doc_with_metadata)) # first 100 list of docIDs
                sorted_by_metadata.extend(first_100_sorted_by_metadata)

    return sorted_by_metadata

"""
Rank phrasal search by tf of the entire phrase.

:param intermediate_result: a dictionary of {doc_id: [positions]}, passed from phrasal_search
:param doc_lengths: a dictionary of { doc_id: doc_length }, to normalise
"""


def rank_phrasal_by_tf(intermediate_result, doc_lengths):
    doc_to_tf = {}  # doc_id: normalised tf
    for doc_id in intermediate_result:
        doc_to_tf[doc_id] = len(intermediate_result[doc_id]) / doc_lengths[doc_id]  # tf / doc_length, normalisation

    ranked = sorted(doc_to_tf.items(), key=lambda x: x[1], reverse=True)  # sorted in desc order by normalised tf
    return [x[0] for x in ranked]  # return only doc_id


"""
Ranking by weighted tf-idf of the query taken as free text.

:param query_tokens: list of stemmed query tokens
:param relevant_doc_ids: a list of relevant doc_ids for the query
:param dictionary: { token: (df, pointer) }
:param postings_file: the file containing postings written in disk
:param doc_lengths: a dictionary of { doc_id: doc_length }, to normalise
"""


def rank_boolean_by_tfidf(query_tokens, relevant_doc_ids, dictionary, postings_file, doc_lengths):
    filtered_postings = {}  # to hold postings filtered based on documents found in relevant_doc_ids

    # first, get all postings for all query tokens
    temp_postings = get_postings(query_tokens, dictionary, postings_file)
    
    # filter only those doc_ids in postings of each token that appear in relevant_doc_ids
    for token in query_tokens:
        if token not in dictionary: # just to bulletproof code, calling method has already ensured this does not happen
            continue

        postings_list = temp_postings[token]
        # only add doc_ids and positions for a token if doc_id is found in relevant_doc_ids
        for doc_id in postings_list:
            if doc_id in relevant_doc_ids:
                positions = postings_list[doc_id]
                if token in filtered_postings:
                    filtered_postings[token][doc_id] = positions
                else:
                    filtered_postings[token] = {doc_id : positions}

    # calculate cosine scores, using algorithms used for vsm search, but on a smaller search space of relevant_doc_ids
    # build query_vector with key: token, value: normalised w_tq of token
    N = len(doc_lengths)  # N is the total number of documents in the corpus
    query_vector = build_query_vector(query_tokens, dictionary, N)

    # calculate scores with key: doc_id, value: cosine score of document corresponding to doc_id
    scores = calculate_cosine_scores(query_vector, filtered_postings, doc_lengths)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)  # sort scores by descending order
    results = [entry[0] for entry in sorted_scores]
    return results

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
            print("found empty query, returning...") # for debugging
            continue

        # check for phrasal query
        if subquery[0] == "\"":
            print("parsed a phrasal query, evaluating...") # for debugging
            parsed_phrasal_query = parse_phrasal_query(subquery)  # returns a list
            parsed_query.append(parsed_phrasal_query)
        else:  # subquery is either single word free text query or multi-word free text query
            if " " in subquery:  # true for multi-word queries
                parsed_multiword_free_text_query = parse_multiword_free_text_query(subquery)  # returns a list
                parsed_query.append(parsed_multiword_free_text_query)

            else:
                # perform query expansion for single word query (boolean or free text)
                parsed_query.append([subquery])

    return parsed_query


def parse_multiword_free_text_query(query):
    """
    Parses multiword free text query by tokenising, stemming, and case folding. Removes stop words from free text query.
    Performs query expansion using synonyms obtained from wordnet if toggled.

    :param query the multiword free text query to be parsed
    :return a list containing individual parsed tokens from the multiword query
    """
    tokens = query.split(" ")  # split query into individual words

    tokens_without_stopwords = [token for token in tokens if not token in stop_words] # stop word removal
    # only remove stop words if free text query contains terms other than stopwords
    # this still allows results for multiword free text search for queries such as 'you are the'
    if tokens_without_stopwords:
        tokens = tokens_without_stopwords

    return tokens


def parse_phrasal_query(query):
    """
    Parse phrasal query by tokenizing, stemming, rejoining and striping off quotation marks

    :param query the phrasal query to be parsed
    :return a list containing the parsed phrasal query
    """
    query = query.strip('"')  # remove quotation marks
    tokens = query.split(" ")  # split query into individual words
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
        print("found empty query, returning...")  # for debugging
        return []
    # check for boolean query
    elif len(query) > 1:
        print("parsed a boolean query, evaluating...")  # for debugging

        # flatten the list of lists into a list of independent queries to be supplied to the boolean AND search function
        flattened_query = [subquery for inner_list in query for subquery in inner_list]

        # stemming and case folding, do not stem the embedded phrasal queries
        stemmed_query = []
        for subquery in flattened_query:
            if " " not in subquery:
                stemmed_query.append(stemmer.stem(subquery.lower()))
            else:
                stemmed_query.append(subquery)

        # call boolean search, which will obtain the postings as required
        results = boolean_search(stemmed_query, dictionary, postings_file, doc_lengths)
        return results

    else:  # no AND, either phrasal query or free text query
        # this should be true as non-boolean searches should only have 1 subquery.
        assert (len(query) == 1)

        # check for phrasal query by checking if there is a space in the first subquery
        first_subquery = query[0][0]
        if " " in first_subquery:
            # obtain individual tokens in phrasal query
            tokenised_phrasal_query = first_subquery.split(" ")

            # call phrasal search, which will obtain the postings as required
            # this phrasal search is not embedded in a boolean search, thus is_boolean = False
            results = phrasal_search(tokenised_phrasal_query, dictionary, postings_file, doc_lengths, False)
            return results

        else:  # free text query, expand query, then run VSM search
            print("parsed a free text query, evaluating...")  # for debugging

            tokenised_free_text_query = query[0]

            tokens = [token.lower() for token in tokenised_free_text_query]  # case folding

            # stem all tokens, return only unique stemmed tokens
            stemmed_tokens = [stemmer.stem(token) for token in tokens]
            unique_stemmed_tokens = []
            for stemmed_token in stemmed_tokens:
                if stemmed_token not in unique_stemmed_tokens:
                    unique_stemmed_tokens.append(stemmed_token)

            # call VSM search, which will obtain the postings as required
            results = vsm_search(unique_stemmed_tokens, dictionary, postings_file, doc_lengths)
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
:param doc_lengths: a dictionary of { doc_id: doc_length }
"""


def vsm_search(query, dictionary, postings_file, doc_lengths):
    print("running vsm search on tokens : ", end='')
    print(query)  # for debugging

    # get postings for each token in query if that token exists in dictionary
    postings = get_postings(query, dictionary, postings_file)

    # build query_vector with key: token, value: normalised w_tq of token
    N = len(doc_lengths)  # N is the total number of documents in the corpus

    query_vector = build_query_vector(query, dictionary, N)

    # calculate scores with key: doc_id, value: cosine score of document corresponding to doc_id
    scores = calculate_cosine_scores(query_vector, postings, doc_lengths)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)  # sort scores by descending order

    # determine threshold for relevance by taking average of percentiles of score values
    # average of percentiles gives a threshold between mean and median
    #
    score_values = [entry[1] for entry in sorted_scores]
    percentiles = []
    for i in range(no_of_quantiles):
        percentiles.append(quantile(score_values, i / no_of_quantiles))
    threshold_score = mean(percentiles)

    results = [entry[0] for entry in sorted_scores if entry[1] > threshold_score]
    return results


"""
Return normalised tf-idf score for given query in ltc scheme.

:param query the query from which query vector is to be built
:param dictionary the dictionary of terms saved to disk, { token: (df, pointer) }
:param N the number of documents in the corpus
:return query vector containing dictionary token as key and normalised w_tq of token as value
"""


def build_query_vector(query, dictionary, N):
    query_vector = defaultdict(float)  # key: token, value: normalised w_tq of token

    # calculate token frequency
    for token in query:
        query_vector[token] += 1

    # calculate weighted token frequency for each token
    w_tq_running_total = 0  # for calculating query length
    for token in query_vector:
        # get df

        if token not in dictionary:
            print("token {token} not in dictionary!".format(token=token))
        df = dictionary[token][0] if token in dictionary else 0

        # calculate idf
        idf = 0.0 if df == 0 else math.log((N / df), 10)

        # calculate logarithmic token frequency
        tf = query_vector[token]
        ltf = 1 + math.log(tf, 10)

        # calculate and store weighted token frequency
        w_tq = ltf * idf
        query_vector[token] = w_tq

        # update w_tq running total for calculating query length
        w_tq_running_total += w_tq ** 2

    # calculate normalised weighted term frequency
    query_length = math.sqrt(w_tq_running_total)
    for token in query_vector:
        query_vector[token] = query_vector[token] / query_length if query_length != 0 else 0  # check for 0 query length

    return query_vector


"""
Return normalised tf-idf score for given query in ltc scheme in the form of a dictionary.
:return dictionary containing document IDs as key and cosine scores as values
"""


def calculate_cosine_scores(query_vector, postings, doc_lengths):
    scores = {}  # key: doc_id, value: cosine score
    for token in postings:
        postings_list = postings[token]
        for doc_id in postings_list:
            # calculate weighted token frequency
            tf = len(postings_list[doc_id])
            ltf = 1 + math.log(tf, 10)

            # update scores
            if doc_id in scores:
                scores[doc_id] += ltf * query_vector[token]
            else:
                scores[doc_id] = ltf * query_vector[token]

    # normalise all scores by dividing by document length
    for doc_id, score in scores.items():
        doc_length = doc_lengths[doc_id]
        scores[doc_id] = score / doc_length if doc_length != 0 else 0  # check for 0 document length

    return scores


# METHODS FOR BOOLEAN 'AND' SEARCH FOR BOOLEAN QUERIES #

"""
Finds intersection of two iterables of doc_ids, sorted in asc order

:param lst1: iterable of token1
:param lst2: iterable of token2

:return: list of common doc_ids
"""


def and_merge(lst1, lst2):
    return sorted(list(set(lst1).intersection(set(lst2))))


"""
Runs boolean search by calling AND merge function on each subquery.

:param query: list of stemmed subquery tokens, phrasal searches given as a phrase without quotation but with space
:param dictionary: { token: (df, pointer) }
:param postings_file: postings.txt
:return result: list of doc_ids
"""


def boolean_search(query, dictionary, postings_file, doc_lengths):
    print("running boolean AND search on tokens : ", end='')
    print(query)  # for debugging

    results = []  # container for results of list intersection
    for i in range(len(query)):
        subquery = query[i]

        # check if subquery is a phrase
        if " " in subquery:
            # run phrasal search after splitting phrasal subquery, returns a list of relevant doc_ids
            tokenised_phrasal_query = subquery.split(" ")
            # this phrasal search is embedded in a boolean search, thus is_boolean = True
            temp_results = phrasal_search(tokenised_phrasal_query, dictionary, postings_file, doc_lengths, True)

            # if intermediate results are empty, immediately return empty list
            if not temp_results:
                return []

        else:
            # if any part of the free text query is not in dictionary, return an empty list, since boolean search 
            # demands exact matches
            if subquery not in dictionary:
                return []
            
            # a single word
            postings = get_postings([subquery], dictionary, postings_file)
            temp_results = postings[subquery] # already checked subquery is in dictionary, so temp_results is not empty

        # merge two lists only if subquery is not the first subquery in query
        if i != 0:
            assert results  # results must not be empty
            results = and_merge(results, temp_results)
        else:
            results = temp_results

    # rank results
    """
    if results:
        # split all phrasal subqueries into individual tokens
        split_query = [token.split(" ") for token in query]
        flattened_query = [token for inner_list in split_query for token in inner_list]
        ranked_results = rank_boolean_by_tfidf(flattened_query, results, dictionary, postings_file, doc_lengths)
    else:
        ranked_results = []
    """

    return results  # ranked list of doc_ids


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

:return result: list of doc_ids
"""


def phrasal_search(tokenised_phrasal_query, dictionary, postings_file, doc_lengths, is_boolean):
    print("running phrasal search on tokens : ", end='')
    print(tokenised_phrasal_query)  # for debugging

    results = {}  # key - doc_id, value - list of positions in document of the last word in phrase

    # retrieve postings of each token in phrasal query
    # postings may be empty, if none of the query tokens are in dictionary
    postings = get_postings(tokenised_phrasal_query, dictionary, postings_file)

    # compare 2-way at a time, that is, compare this token with the preceding token
    for i in range(len(tokenised_phrasal_query)):
        token = tokenised_phrasal_query[i]

        # immediately return empty list if token is not in dictionary
        if token not in dictionary:
            return []

        token_postings = postings[token]  # get { doc_id: [positions] }

        # continue loop if token is the first token in phrase after setting temp_results to postings of first token
        if i == 0:
            results = token_postings
        else:
            # if results is ever empty, it means the phrase is not in corpus, return empty list
            if not results:
                return []

            # token is not first token, continue with phrasal search
            # find intersection of doc_ids as a list
            shared_docs = and_merge(results.keys(), token_postings.keys())

            intermediate_results = {}  # container to hold intermediate results of positional intersect
            for doc_id in shared_docs:
                p1 = results[doc_id]  # list of positions of last word in previous iteration
                p2 = token_postings[doc_id]  # positions of current token

                consecutive_positions = get_consecutives(p1, p2)
                if consecutive_positions:
                    intermediate_results[doc_id] = consecutive_positions

            results = intermediate_results

    if not is_boolean:
        return rank_phrasal_by_tf(results, doc_lengths)

    return list(results.keys())


def expand_query(query_tokens):
    # these query_tokens are case-folded, but not stemmed
    pos_tagged_tokens = nltk.pos_tag(query_tokens) # tag parts of speech for each token

    # only synonyms for nouns in the given query will be considered
    # this dictionary is to map nltk's pos_tag method with synsets method
    accepted_pos = {'NN' : wn.NOUN}
    filtered_pos_tagged_tokens = [token for token in pos_tagged_tokens if token[1] in accepted_pos] # get list of tuples

    synonyms = []
    synsets = [wn.synsets(token[0], pos=accepted_pos[token[1]]) for token in filtered_pos_tagged_tokens]
    for synset in synsets:
        for lemma in synset:
            lemma_name = lemma.name() # format - word.pos.index, need to delimit by .
            split_lemma_name = lemma_name.split(".") # first item in this list is the synonym we want
            # some synonyms have two or more words delimited by _, just ignore these
            if "_" not in split_lemma_name[0]:
                synonym = split_lemma_name[0]
                synonyms.append(synonym)

    unique_synonyms = list(set(synonyms))
    return unique_synonyms
