import math
from searching_utils import get_postings, calculate_cosine_scores, build_query_vector

"""
Extracting tokens and their associated tf-idf weights
from trimmed_documents, stored in dictionary.txt.

:param documents: { docID: [ (token: tf.idf) ] }
"""
def document_vectors(documents):
    doc_vectors = {}
    for docID in documents:
        doc_vectors[docID] = {}
        content = documents[docID] # {term: tf.idf}

        for token, tfidf in content:
            doc_vectors[docID][token] = tfidf

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

    for docID in top_k:
        tokens = doc_vectors[docID]

        for token in tokens:
            if token not in centroid:
                centroid[token] = tokens[token] # normalised tf-idf of token in this doc
            else:
                centroid[token] += tokens[token] # add normalised tf-idf of token in this doc

    for token in centroid:
        centroid[token] /= k

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

    doc_vectors = document_vectors(documents)

    centroid = find_centroid(top_k, doc_vectors) # { token: tf-idf of token in centroid }

    new_query_vector = {}
    for token in centroid:
        if token not in query_vector: # also need to include tokens not in query, then tf-idf of this token is 0 in q0
            new_query_vector[token] = beta * centroid[token]
        else:
            new_query_vector[token] = alpha * query_vector[token] + beta * centroid[token]

    print("size of new query vector: {n}".format(n=len(new_query_vector)))
    print("new query vector:")
    print(list(new_query_vector.items())[:20])

    postings = get_postings(new_query_vector, dictionary, postings_file) # tf-idf of these terms of all documents

    print("size of postings: {n}".format(n=len(postings)))

    scores = calculate_cosine_scores(new_query_vector, postings, doc_lengths)

    sorted_scores = sorted(scores.items(), key=lambda x: x[1]) # x[1] is the score

    print("scores:")
    print(sorted_scores[:20])

    return list(map(lambda x: x[0], sorted_scores)) # list of docIDs
