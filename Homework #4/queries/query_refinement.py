import math
from searching_utils import get_postings

"""
Finds the normalised tf.idf values for all tokens, and stores it in a dictionary.

:param tokens: tokens to find
"""
def get_normalised_tf_idf(tokens, dictionary, postings, doc_lengths):
    scores = {}  # key: docID, value: cosine score
    for token in tokens:
        for docID in postings[token]:
            # calculate weighted token frequency
            tf = len(postings[token][docID])
            ltf = 1 + math.log(tf, 10)

            idf = math.log(1/dictionary[token][0], 10) # lg(1/df)
            # update scores
            if token in scores:
                scores[token] += ltf * idf
            else:
                scores[token] = ltf * idf

    # normalise all scores by dividing by document length
    for token, score in scores.items():
        doc_length = doc_lengths[docID]
        scores[token] = score / doc_length

    return scores

"""
Rocchio, assuming documents have been indexed
:param top_k: list of top relevant docIDs
:param documents: indexed documents { docID: content }
"""
def rocchio(top_k, dictionary, postings_file, doc_lengths, documents):
    # index document with { docID: { token: tf.idf } }
    # find centroid with top_k doc
    # 1. sum the tf.idf of each token of all relevant docs
    #   1.1 for tokens that do not exist in a doc, add 0
    # 2. divide each sum by no. of docs
    # 3. multiply by weight and add to original query
    # 4. Take the new dictionary of { token: value} and run cosine similarity on all docs agn.

    tokens = set() # unique terms

    for docID in top_k:
        # all documents in top_k are indexed in documents
        content = documents[docID] # content of document

        for token in content:
            tokens.add(token)

    tokens = list(tokens)

    postings = get_postings(list(tokens), dictionary, postings_file)

    for token in tokens:
        token_with_tf_idf = get_normalised_tf_idf(tokens, dictionary, postings_file, doc_lengths) # { token: tf.idf }


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
