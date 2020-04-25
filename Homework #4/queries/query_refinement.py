import math
from searching_utils import get_postings

"""
Finds the normalised tf.idf values for all tokens, and stores it in a dictionary.

:param tokens: tokens to find
"""
def get_total_normalised_tf_idf(tokens, dictionary, postings, doc_lengths):
    scores_for_combined_vector = {}  # key: docID, value: cosine score
    for token in tokens:
        for docID in postings[token]:
            # calculate weighted token frequency
            tf = len(postings[token][docID])
            ltf = 1 + math.log(tf, 10)

            idf = math.log(1/dictionary[token][0], 10) # lg(1/df)
            doc_length = doc_lengths[docID]

            # update scores, normalising all scores by dividing by document length for each doc
            if token in scores_for_combined_vector:
                scores_for_combined_vector[token] += ltf * idf / doc_length
            else:
                scores_for_combined_vector[token] = ltf * idf  / doc_length

    return scores_for_combined_vector

"""
Rocchio, assuming documents have been indexed

:param query: { query_token: original_tf.idf } 
:param top_k: list of top relevant docIDs
:param documents: indexed documents { docID: content }
"""
def rocchio(query, top_k, dictionary, postings_file, doc_lengths, documents):

    alpha = 0.2 # magic number 1
    beta = 0.3 # magic number 2

    # index document with { docID: { token: tf.idf } }
    # find centroid with top_k doc
    # 1. sum the tf.idf of each token of all relevant docs
    # 2. divide each sum by no. of docs
    # 3. multiply by weight and add to original query
    # 4. Take the new dictionary of { token: value } and run cosine similarity on all docs agn.

    tokens = set() # unique terms

    for docID in top_k:
        # all documents in top_k are indexed in documents
        content = documents[docID] # content of document

        for token in content:
            tokens.add(token)

    tokens = list(tokens)

    postings = get_postings(list(tokens), dictionary, postings_file)

    tokens_dict_with_tf_idf = get_total_normalised_tf_idf(tokens, dictionary, postings, doc_lengths) # { token: total_normalised_tf.idf }

    # divide by no. of docs
    for token in tokens_dict_with_tf_idf:
        tokens_dict_with_tf_idf[token] /= len(top_k)

    new_query_vector = {}
    for token in tokens_dict_with_tf_idf:
        if token not in query:
            new_query_vector[token] = beta * tokens_dict_with_tf_idf[token]
        else:
            new_query_vector[token] = alpha * query[token] + beta * tokens_dict_with_tf_idf[token]

    find_cosine_similarity_against_docs_agn

"""
Assumes top-k searches are relevant, and evaluates relevance feedback accordingly.
:param dictionary: to get df
:param postings_file: to get tf
"""
def blind_relevance_feedback(top_k, dictionary, postings_file, doc_lengths):
    # of all the common terms in these docs, find their tf-idf and take the top 20-30

    # find intersection of all words in top_k docs
    # filter by a certain threshold for tf-idf
    # add these words to the query
    # run search agn

    pass
