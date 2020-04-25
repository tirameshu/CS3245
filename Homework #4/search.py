import getopt
import pickle
import sys
import time

from searching_utils import parse_query, evaluate_query

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
        dictionary = pickle.load(dict) # contains a list of Term objects
        metadata = pickle.load(dict)

    with open(queries_file, 'r') as query_file, open(results_file, 'w') as result_file:
        query_content = query_file.read().splitlines()

        # check for empty query
        if not query_content:
            result_file.write('\n')
            return

        query = query_content[0] # first line in query file is the query
        print("searching " + query) # for debugging

        # evaluate query to obtain results
        parsed_query = parse_query(query)

        # returned result will be alr ranked:
        # free text: ranked by VSM
        # non-boolean phrase: ranked by tf of phrase
        #
        results = evaluate_query(parsed_query, dictionary, doc_lengths, postings_file)

        print("retrieving " + str(len(results)) + " relevant results") # for debugging

        # TODO order relevant documents by processing metadata

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
