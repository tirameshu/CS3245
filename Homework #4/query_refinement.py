import math
from searching_utils import get_postings, calculate_cosine_scores, build_query_vector

"""
Create a document vector for allll documents,
storing each token in a document and their normalised tf-idf weight.
:param postings_file: postings.txt
"""
def document_vectors(documents, dictionary):
    doc_vectors = {}
    N = len(documents)
    i = 0
    for docID in documents:
        if i == 4:
            break
        print(docID)
        doc_vectors[docID] = {}
        content = documents[docID]

        content_vector = build_query_vector(content, dictionary, N)

        doc_vectors[docID] = content_vector

        i += 1

    return doc_vectors

"""
Finds centroid of top_k docs (assumed to be relevant) by
summing their vectors and dividing by k

:param doc_vectors: { docID: { token: tf-idf } }

:return centroid: centroid of top_k vectors
"""
def find_centroid(top_k, doc_vectors):
    print("in centroid")
    k = len(top_k)
    centroid = {}

    n = 0 # for testing only
    for docID in top_k:
        if docID > 246404: # for testing only
            continue # for testing only
        tokens = doc_vectors[docID]

        for token in tokens:
            if token not in centroid:
                centroid[token] = tokens[token] # normalised tf-idf of token in this doc
            else:
                centroid[token] += tokens[token] # add normalised tf-idf of token in this doc
        n += 1

    for token in centroid:
        centroid[token] /= n

    return centroid

"""
Rocchio, assuming documents have been indexed

:param query: { query_token: original_tf.idf } 
:param top_k: list of top relevant docIDs
:param documents: indexed documents { docID: content }
"""
def rocchio(query_vector, top_k, dictionary, postings_file, doc_lengths, documents):

    alpha = 0.2 # magic number 1
    beta = 0.3 # magic number 2

    # index document with { docID: { token: tf.idf } }
    # find centroid with top_k doc
    # 1. sum the tf.idf of each token of all relevant docs
    # 2. divide each sum by no. of docs
    # 3. multiply by weight and add to original query
    # 4. Take the new dictionary of { token: value } and run cosine similarity on all docs agn.

    doc_vectors = document_vectors(documents, dictionary)

    centroid = find_centroid(top_k, doc_vectors) # { token: tf-idf of token in centroid }

    new_query_vector = {}
    for token in centroid:
        if token not in query_vector: # also need to include tokens not in query, then tf-idf of this token is 0 in q0
            new_query_vector[token] = beta * centroid[token]
        else:
            new_query_vector[token] = alpha * query_vector[token] + beta * centroid[token]

    postings = get_postings(new_query_vector, dictionary, postings_file) # tf-idf of these terms of all documents

    scores = calculate_cosine_scores(new_query_vector, postings, doc_lengths)

    sorted_scores = sorted(scores.items(), key=lambda x: x[1]) # x[1] is the score

    return list(map(lambda x: x[0], sorted_scores)) # list of docIDs

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
