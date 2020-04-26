import getopt
import pickle
import sys
import time

from query_refinement import rocchio
from searching_utils import parse_query, evaluate_query, build_query_vector, sort_results_by_metadata

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q query-file -o output-file-of-results")

"""
Runs search by extracting query from query file, evaluating it, and writing the results to result file

:param dict_file the file containing dictionary written in disk
:param postings_file the file containing postings written in disk
:param queries_file the file containing the query
:param results_file the file to write the results to
"""
def run_search(dict_file, postings_file, queries_file, results_file):
    print("searching...") # for debugging
    # load contents from dictionary saved to disk
    with open(dict_file, 'rb') as dict:
        # retrieve document lengths and vocabulary
        doc_lengths = pickle.load(dict)
        dictionary = pickle.load(dict) # contains a list of
        documents = pickle.load(dict)
        metadata = pickle.load(dict)

    with open(queries_file, 'r') as query_file, open(results_file, 'w') as result_file:
        query_content = query_file.read().splitlines()

        # check for empty query
        if not query_content:
            print("no query found")  # for debugging
            result_file.write('\n')
            return

        query = query_content[0] # first line in query file is the query
        print("searching for : " + query) # for debugging

        # evaluate query to obtain results
        parsed_query = parse_query(query)

        # returned result will be alr ranked:
        # free text: ranked by cosine similarity score between query and set of documents in corpus
        # stand-alone phrasal query: ranked by tf of phrase
        # boolean query: ranked by cosine similarity of all tokens in query to set of retrieved documents

        results = evaluate_query(parsed_query, dictionary, doc_lengths, postings_file)
        print("performed initial round of retrieval.") # for debugging

        # TODO query refinement
        print("commencing query refinement...") # for debugging

        # perform query expansion using synonyms from Wordnet for free text queries only
        # free text queries are those with only one list in parsed_query list and
        #if len(parsed_query) == 1 and " " not in parsed_query[0][0]:

        # rocchio

        k = 50
        flattened_query = [subquery for inner_list in parsed_query for subquery in inner_list]
        # take out individual tokens

        query_vector = build_query_vector(flattened_query, dictionary, len(query))

        results = rocchio(query_vector, results[:k], dictionary, postings_file, doc_lengths, documents)

        print("retrieving " + str(len(results)) + " relevant results") # for debugging

        # order relevant documents by processing metadata
        # first rank by whether any part of the query is in the title, as this is the least important order
        # then by date, which are tiered based on how recent it is
        # lastly by court, as this is the primary/ overall order
        results = sort_results_by_metadata(results, metadata, flattened_query)

        # write results to disk
        result_string = " ".join(str(i) for i in results)
        print("writing results to disk...") # for debugging
        result_file.write(result_string + '\n')

dictionary_file = postings_file = query_file = output_file_of_results = None

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
        query_file = a
    elif o == '-o':
        output_file_of_results = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or query_file == None or output_file_of_results == None :
    usage()
    sys.exit(2)

start_time = time.time()  # clock the run
run_search(dictionary_file, postings_file, query_file, output_file_of_results)
end_time = time.time()
print('search completed in ' + str(round(end_time - start_time, 2)) + 's')
