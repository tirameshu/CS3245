from collections import defaultdict
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
import math
import pickle

from searching_utils import build_query_vector

"""
Collects all tokens from a given data string after performing tokenizing, case folding, alphanumeric filtering, and
stemming.

:param data data string to be tokenized
"""
def collect_tokens(data):
    tokens = []
    stemmer = PorterStemmer()  # use Porter stemmer for stemming

    # collect tokens from data
    sentences = sent_tokenize(data)  # sentence tokenizing
    for sentence in sentences:
        words = word_tokenize(sentence)  # word tokenizing
        for word in words:
            # only process alphanumeric tokens
            if word.isalnum():
                word = word.lower()  # case folding
                word = stemmer.stem(word)  # stemming
                tokens.append(word)
    return tokens


"""
Updates index with information from each token in the given list of tokens. Returns a mapping of
all unique terms in this document along with their term frequencies.

:param index index to be updated
:param tokens the tokens to be processed
:param doc_id the document ID of the document the tokens are found in
:return a dictionary consisting of unique terms and their term frequencies for calculating document length
"""
def process_tokens(index, tokens, doc_id):
    term_frequencies = defaultdict(int)  # to store document vector and calculate doc_length

    for pos in range(len(tokens)):  # pos refers to positional index of a token in the document
        token = tokens[pos]
        term_frequencies[token] += 1

        if token in index:
            # if token exists in index, update its dictionary of Nodes
            if doc_id in index[token]:
                # if docID exists in index, add pos to its list
                index[token][doc_id].append(pos)
            else:
                # add docID to index
                index[token][doc_id] = [pos]

        else:
            # if token does not exist in index, create new entry in index
            index[token] = {doc_id: [pos]}

    return term_frequencies


"""
Calculates document length given a list of term frequencies
"""
def calculate_doc_length(tfs):
    running_sum = 0
    for tf in tfs:
        running_sum += (1 + math.log(tf, 10)) ** 2  # tf is guaranteed to be at least 1
    return math.sqrt(running_sum)


"""
Writes postings and dictionary to disk

:param index: the index from which postings and dictionary are to be extracted
:param doc_lengths: dictionary of doc_lengths to be written to dictionary file in disk
:param documents: dictionary of top tokens from each document to be written to dictionary file in disk
:param metadata: dictionary of metadata to be written to dictionary file in disk
:param out_dict: target output file to write dictionary to
:param out_postings: target output file to write postings to
"""
def write_to_disk(index, doc_lengths, documents, metadata, out_dict, out_postings):
    print("writing to disk")  # for debugging

    terms = {}  # terms to be written to dictionary in disk. key - term, value - (df, pointer)

    # write postings to disk
    with open(out_postings, 'wb') as postings:
        print("writing postings to disk")  # for debugging
        for token in index:
            print("writing postings for " + token)  # for debugging

            # { docID: positions } converted to tuples and sorted by doc_id
            # then dict reconstructed from it
            postings_list = dict((k, v) for k, v in sorted(index[token].items(), key=lambda x: x[0]))

            # extract token information such as document frequency and pointer to postings
            df = len(index[token])
            pointer = postings.tell()
            terms[token] = (df, pointer)

            print("dumping")
            pickle.dump(postings_list, postings)  # save postings to disk

    # filter tokens in documents to store only the top 100 by weighted tf-idf score
    k = 100
    trimmed_documents = defaultdict(list)

    N = len(documents)
    for docID in documents:
        content = documents[docID]
        content_vector = build_query_vector(content, terms, N)  # { token: tf.idf }

        assert content_vector

        # sorted list of unique tokens in doc
        # x[1] = tf.idf, in desc order
        sorted_content = sorted(list(content_vector.items()), key=lambda x: x[1], reverse=True)

        # assuming some documents do not contains > 100 tokens
        top_k_tokens = filter(lambda x: x[1] >= sorted_content[min(len(sorted_content) - 1, k - 1)][1], sorted_content)

        for token in top_k_tokens:
            trimmed_documents[docID].append(token)

    # write dictionary to disk
    # the pickled dictionary file contains the following data in order - doc_lengths, terms, documents, metadata
    with open(out_dict, 'wb') as dictionary:
        print("writing dictionary to disk")  # for debugging
        pickle.dump(doc_lengths, dictionary)
        pickle.dump(terms, dictionary)
        pickle.dump(trimmed_documents, dictionary)
        pickle.dump(metadata, dictionary)
