import linecache
import math
from collections import defaultdict

from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.stem import PorterStemmer
from node import Node


def collect_tokens(file_path_string):
    """
    Collects all tokens from a given file after performing tokenizing, case folding, and stemming.

    @param file_path_string a string corresponding to the file to be tokenized
    """
    tokens = []
    stemmer = PorterStemmer() # use Porter stemmer for stemming

    # get all lines from given document
    lines = linecache.getlines(file_path_string)

    # collect tokens from each line
    for line in lines:
        sentences = sent_tokenize(line) # sentence tokenizing
        for sentence in sentences:
            words = word_tokenize(sentence) # word tokenizing
            for word in words:
                word = word.lower() # case folding
                word = stemmer.stem(word) # stemming
                tokens.append(word)

    return tokens

def process_tokens(tokens, doc_id, index):
    """
    Updates dictionary and postings with information from each token in the given list of tokens. Returns a mapping of
    all unique terms in this document along with their term frequencies.

    @param token the token to be processed
    @param doc_id the document ID of the document the token is found in
    @param dictionary dictionary to be updated
    @param postings postings to be updated
    @return a dictionary consisting of unique terms and their term frequencies
    """
    term_frequencies = defaultdict(int) # to calculate doc_length

    for pos in range(len(tokens)): # pos refers to positional index of a token in the document
        token = tokens[pos]
        term_frequencies[token] += 1

        if token in index:
            # if token exists in index, update its Nodes
            if doc_id in index[token]:
                # if doc_id exists among the token's Nodes, update that Node with positional index
                index[token][doc_id].add_position(pos)
            else:
                # doc_id does not exist among the token's Nodes, create a new Node
                index[token][doc_id] = Node(doc_id, pos)

            #postings_index = dictionary.get_pointer(token)
            #df_has_changed = postings.update_entry(doc_id, postings_index) # returns true if df of token changed
            #if df_has_changed:
            #dictionary.increment_df(token)

        else:
            # if token does not exist in index, create new entry in index
            index[token] = {doc_id : Node(doc_id, pos)}

            #postings.add_entry(doc_id)
            #postings_index = postings.get_length() - 1
            #dictionary.add_unique_term(token, postings_index)

    return term_frequencies

def calculate_doc_length(tfs):
    """
    Calculates document length given a list of term frequencies
    """
    sum = 0
    for tf in tfs:
        sum += (1 + math.log(tf, 10))**2 # tf is guaranteed to be at least 1
    return math.sqrt(sum)