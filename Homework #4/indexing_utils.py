from collections import defaultdict
import math
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.stem import PorterStemmer
import pickle

from node import Node
from term import Term


def collect_tokens(data):
    """
    Collects all tokens from a given data string after performing tokenizing, case folding, and stemming.

    :param data data string to be tokenized
    """
    tokens = []
    stemmer = PorterStemmer() # use Porter stemmer for stemming

    # collect tokens from data
    sentences = sent_tokenize(data) # sentence tokenizing
    for sentence in sentences:
        words = word_tokenize(sentence) # word tokenizing
        for word in words:
            word = word.lower() # case folding
            word = stemmer.stem(word) # stemming
            tokens.append(word)

    return tokens

def process_tokens(index, tokens, doc_id):
    """
    Updates index with information from each token in the given list of tokens. Returns a mapping of
    all unique terms in this document along with their term frequencies.

    :param index index to be updated
    :param tokens the tokens to be processed
    :param doc_id the document ID of the document the tokens are found in
    :return a dictionary consisting of unique terms and their term frequencies for calculating document length
    """
    term_frequencies = defaultdict(int) # to calculate doc_length

    for pos in range(len(tokens)): # pos refers to positional index of a token in the document
        token = tokens[pos]
        term_frequencies[token] += 1

        if token in index:
            # if token exists in index, update its dictionary of Nodes
            if doc_id in index[token]:
                # if Node exists in index, update that Node with positional index
                index[token][doc_id].add_position(pos)
            else:
                # add Node to index
                index[token][doc_id] = Node(doc_id, pos)

        else:
            # if token does not exist in index, create new entry in index
            index[token] = {doc_id : Node(doc_id, pos)}

    return term_frequencies

def calculate_doc_length(tfs):
    """
    Calculates document length given a list of term frequencies
    """
    sum = 0
    for tf in tfs:
        sum += (1 + math.log(tf, 10))**2 # tf is guaranteed to be at least 1
    return math.sqrt(sum)

def write_to_disk(index, doc_lengths, titles, courts, out_dict, out_postings):
    """
    Writes postings and dictionary to disk

    @param index the index from which postings and dictionary are to be extracted
    @param doc_lengths dictionary of doc_lengths to be written to dictionary file in disk
    @param titles dictionary of titles to be written to dictionary file in disk
    @param courts dictionary of courts to be written to dictionary file in disk
    @param out_dict target output file to write dictionary to
    @param out_postings target output file to write postings to
    """
    terms = []  # list of Terms to be written to dictionary in disk

    # write postings to disk
    with open(out_postings, 'wb') as postings:
        for token in index:
            # obtain postings list of Nodes sorted by doc_id
            postings_list = [entry[1] for entry in sorted(index[token].items())] # entry[1] corresponds to Node

            # update next and skip Nodes for each Node in postings list
            update_nodes(postings_list)

            # extract Term information such as document frequency and pointer to postings
            df = len(index[token])
            pointer = postings.tell()
            terms.append(Term(token, df, pointer))  # add Term to list of terms

            pickle.dump(postings_list, postings)  # save postings to disk

    # write dictionary to disk
    # the pickled dictionary file contains the following data in order - doc_lengths, titles, courts, terms
    with open(out_dict, 'wb') as dictionary:
        pickle.dump(doc_lengths, dictionary)
        pickle.dump(titles, dictionary)
        pickle.dump(courts, dictionary)
        pickle.dump(terms, dictionary)

def update_nodes(postings):
    """
    Updates the next and skip nodes for all nodes in the given postings list

    @param postings list of nodes to be updated
    """
    # follow heuristic where sqrt(l) skip pointers are evenly placed on the a postings list of length l
    len_postings = len(postings)
    skip_step = math.floor(math.sqrt(len_postings))

    for i in range(len_postings):
        node = postings[i]

        # set skip pointers only for multiples of skip_step
        if i % skip_step == 0:
            skip_node = postings[min(i+skip_step, len_postings - 1)]
            if skip_node != node:
                node.set_skip(skip_node)

        # set next
        if i == len_postings - 1:
            return # last node reached, last node has no next, so return
        next_node = postings[i+1]
        node.set_next(next_node)
