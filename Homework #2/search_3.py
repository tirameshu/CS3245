#!/usr/bin/python3
import math
import re
import sys
import getopt
import pickle

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer

dictionary = {}

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

class Node:
    def __init__(self, docID):
        self.docID = docID # int
        self.skip = None
        self.next = None

    def set_next(self, node):
        self.next = node

    def set_skip(self, node):
        self.skip = node

    def get_next(self):
        return self.next

    def get_skip(self):
        if (self.has_skip):
            return self.skip

    def has_next(self):
        return self.next != None and type(self.next) == Node

    def has_skip(self):
        return self.skip != None and self.skip != self

"""
Returns a list of nodes, to support AND merge
"""
def indiv_search(term):
    # print(list(dictionary.items())[:4])
    # print("indiv_search for: ")
    # print(term)
    if term not in dictionary:
        # print("this term not in dict: " + term)
        return []
    return dictionary[term] # nodes

"""
Dictionary contains no symbols; situations like "hi!" is tokenized into "hi", "!"
So queries containing non-alpha chars will render no results anyway, similar to searching for empty string
"""
def process_query_term(query_term):
    ps = PorterStemmer()
    if query_term.isalpha():
        term = query_term.strip()
        term = ps.stem(term)
        return term.lower()
    return ""

"""
Set up skip pointers for intermediate lists
Arg: list of nodes
Returns sorted list w skip pointers
"""
def setup_skip_pointers(lst):
    result = []
    lst.sort(key=lambda x: x.docID) # just in case
    # print("list at start of setup: ")
    # print(lst[:4])

    L = len(lst)
    sqrt_L = math.floor(math.sqrt(L))

    for i in range(L):
        node = lst[i]
        if i % sqrt_L == 0: # only for multiples of sqrt_L
            skip_to = lst[min(i+sqrt_L, L-1)]
            if skip_to != node:
                node.set_skip(skip_to)

        # set next
        if i == L-1:
            break # only last one has no next
        next = lst[i+1]
        node.set_next(next)
        result.append(node)

    # print("list at end of setup: ")
    # print(result[:4])

    return result

"""
Term: either a node or a list of nodes
Returns a sorted list of all docs (NODES) that do NOT contain this term
"""
def not_search(term, dict):
    # print("not_search for: ")
    # print(term)
    result = []

    dict.seek(0) # reset

    if type(term) != list:
        posting = indiv_search(term) # list of nodes

    else:
        posting = term

    # if (len(posting) > 0):
        # print("posting not empty for term ")
        # print(term)

    all_files_int = list(map(lambda x: int(x), word_tokenize(dict.readline().strip()))) # assume sorted
    # print("all files:")
    # print(all_files_int[:4])

    if posting:
        node = posting[0]
        for file_no in all_files_int:
            if file_no == node.docID: # both int
                node = node.get_next()
            else:
                if file_no > node.docID:
                    node = node.get_next()
                result.append(Node(file_no))
    else:
        for file_no in all_files_int:
            result.append(Node(file_no))

    result = setup_skip_pointers(result)
    # print("result of not search for term")
    # print(term)
    # print(result[:4])
    return result

"""
args: list of nodes, both sorted bcos directly taken from dictionary
returns: sorted list of nodes
"""
def and_merge(lst1, lst2):
    # lst1.sort(key=lambda x: x.docID)
    # print(list(map(lambda x: x.docID, lst1))[:4])
    # lst2.sort(key=lambda x: x.docID)
    # print(list(map(lambda x: x.docID, lst2))[:4])

    node1 = lst1[0]
    node2 = lst2[0]
    result = []

    while node1 != None and node2 != None:
        # print("node1: " + str(node1.docID))
        # print("node2: " + str(node2.docID))
        if node1.docID < node2.docID:
            if node1.has_skip():
                skip_node = node1.get_skip()
                # print("node 1 skips to " + str(skip_node.docID) + " ?")
                if skip_node.docID < node2.docID: # utilise skip pointer
                    node1 = skip_node
                else:
                    node1 = node1.get_next()
            else:
                node1 = node1.get_next()

        elif node2.docID < node1.docID:
            if node2.has_skip():
                skip_node = node2.get_skip()
                # print("node 2 skips to " + str(skip_node.docID) + " ?")
                if skip_node.docID < node1.docID:  # utilise skip pointer
                    node2 = skip_node
                    # print("node 2 skips!")
                else:
                    node2 = node2.get_next()
            else:
                node2 = node2.get_next()
        else: # increment by 1 when match found
            result.append(node1) # save node
            node1 = node1.get_next()
            node2 = node2.get_next()

        # print("result: ")
        # print(result)
    return result

    # s1 = set(lst1)
    # s2 = set(lst2)
    # result = list(s1.intersection(s2))
    # result.sort(key=lambda x: int(x))
    #
    # return result

"""
args: list of nodes, both sorted bcos directly taken from dictionary
returns: sorted list of nodes
"""
def or_merge(lst1, lst2):
    result = []

    if lst1 and not lst2:
        return lst1

    if lst2 and not lst1:
        return lst2

    node1 = lst1[0]
    node2 = lst2[0]
    while node1 != None and node2 != None:
        if node1.docID == node2.docID:
            result.append(node1)
            node1 = node1.get_next()
            node2 = node2.get_next()
        elif node1.docID < node2.docID:
            result.append(node1)
            node1 = node1.get_next()
        else:
            result.append(node2)
            node2 = node2.get_next()

    # print("result for OR merge ")
    # print(result[:4])
    return result

"""
Args: oper1 op oper2
Merges lists based on op
Returns: sorted list of nodes
"""
def op_merge(args):
    # print("args: ")
    # print(args)

    # operators = ["AND", "OR"]
    oper1, op, oper2 = args # str

    if type(oper1) != list:
        term1 = process_query_term(oper1)
        # print("term 1 in OR search: " + term1)
        lst1 = indiv_search(term1)
    else:
        lst1 = oper1

    if type(oper2) != list:
        term2 = process_query_term(oper2)
        # print("term 2 in OR search: " + term2)
        lst2 = indiv_search(term2)
    else:
        lst2 = oper2

    if op == "NOT":
        print("impossible; a \"NOT\" got away!!")
        return []
    elif op == "AND":
        return and_merge(lst1, lst2)
    elif op == "OR":
        # print("conducting OR search")
        return or_merge(lst1, lst2)
    else:
        print("unknown op")
        return []




"""
Merge a whole bunch of terms with no brackets
eg term1 AND term2 OR NOT term3

Returns empty list when no doc fulfills query

to_merge can contain nested list (alr processed queries),
as simple_merge can be called recursively. 

Continues to next query term is current one is non-alpha/ empty str
"""
def simple_merge(to_merge, dict):
    # print("to merge: ")
    # print(to_merge)
    stack = []

    not_flag = []
    not_flag.append(False)

    for query_term in to_merge:
        # print("simple_merge for loop:")
        # print(stack)

        if query_term == "NOT":
            not_flag[0] = True
        else:
            if not_flag[0]:
                term = process_query_term(query_term)
                if not term:
                    continue
                lst = not_search(term, dict) # list of str
                #  ("not list:")
                # print(lst[:3])
                stack.append(lst)
                not_flag[0] = False
            else:
                stack.append(query_term)
                # print("line 137: ")
                # print(stack)
    # all "NOT"s processed
    # remaining op all binary
    # print("all NOTs processed, stack now:")
    # print(stack)

    while len(stack) > 1 and "AND" in stack:
        # print("simple_merge AND loop")
        index = stack.index("AND")
        args = [stack[index-1], stack[index], stack[index+1]]
        result = op_merge(args)
        stack[index-1] = result # insert back
        del stack[index:index + 2]

    while len(stack) > 1 and "OR" in stack:
        # print("simple_merge OR loop")
        index = stack.index("OR")
        args = [stack[index-1], stack[index], stack[index+1]]
        result = op_merge(args)
        stack[index - 1] = result  # insert back
        del stack[index:index + 2]

    result = stack.pop()
    return result

"""
Only look through the dict file once to get all lists of the query terms
"""
def get_all_relevant_lists(query_terms, dict, postings):
    # reset dict first
    dict.seek(0)

    operators = ["(", ")", "NOT", "AND", "OR"]
    query_terms = list(map(lambda x: process_query_term(x), filter(lambda x: x not in operators, query_terms)))

    # search for all query terms in dictionary
    # add to result as long as a desired term is encountered to reduce looping times
    for line in dict:
        elements = line.split(" ")
        term = elements[0]
        if term in query_terms and term not in dictionary: # don't update repeatedly
            pointer = int(elements[2])
            postings.seek(pointer)
            docs = pickle.load(postings) # list of nodes

            docs.sort(key=lambda x: x.docID) # sort from the start

            assert isinstance(docs, list)
            dictionary[term] = docs

"""
Just to flatten and remove brackets
() > NOT > AND > OR 
"""
def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    dict = open(dict_file, "r")
    postings = open(postings_file, "rb")
    queries = open(queries_file, "r")
    results = open(results_file, "a+")

    """
    Assumes that query individual words joined by logic operators, ie no bill gates AND vista
    Does NOT assume that only logic operators are all uppercase
    """
    for query_line in queries:
        stack = [] # renew for every new query_line
        to_merge = []
        sentence = sent_tokenize(query_line)
        query_terms = word_tokenize(sentence[0])

        # fill up dictionary first
        get_all_relevant_lists(query_terms, dict, postings)

        if len(query_terms) == 1: # non-logical searches
            result = indiv_search(query_terms[0])
        else:
            for query_term in query_terms:
                # print("run_search:")
                # print(stack)
                # brackets take priority
                if query_term == ")":
                    term = stack.pop()
                    while term != "(": # process bracketed exp first
                        to_merge.insert(0, term)
                        term = stack.pop()
                    # print("line 210: to merge ")
                    # print(to_merge)

                    """
                    merging!
                    """
                    result = simple_merge(to_merge, dict)  # list of docIDs
                    stack.append(result)  # stack can become nested list
                else:
                    stack.append(query_term)
            # by the end of this loop, the stack should just be
            # A AND NOT B OR C[] kind of thing

            # print("end of run_search loop, stack:")
            # print(stack)

            """
            merging!
            """
            result = simple_merge(stack, dict)

        if result:
            # if type(result) == str:
                # print("result is string: " + result)
            result.sort(key=lambda x: x.docID)
            results.write(" ".join(map(lambda x: str(x.docID), result)) + "\n")
        else:
            results.write("\n")

    dict.close()
    postings.close()
    queries.close()
    results.close()


dictionary_file = postings_file = file_of_queries = file_of_output = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
