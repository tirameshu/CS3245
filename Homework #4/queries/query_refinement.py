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

"""
Rocchio
:param documents: indexed documents { docID: content }
"""
def rocchio(top_k, dicitionary, postings_file, doc_lengths, documents):
    # index document with { docID: { token: tf.idf } }
    # find centroid with top_k doc
    # 1. sum the tf.idf of each token of all relevant docs
    #   1.1 for tokens that do not exist in a doc, add 0
    # 2. divide each sum by no. of docs
    # 3. multiply by weight and add to original query
    # 4. Take the new dictionary of { token: value} and run cosine similarity on all docs agn.

    pass
