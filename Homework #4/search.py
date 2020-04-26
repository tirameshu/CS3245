import getopt
import pickle
import sys
import time

from query_refinement import rocchio
from searching_utils import parse_query, evaluate_query, build_query_vector, sort_results_by_metadata, expand_query

query_expansion_toggle = False # expand query using wordnet synonyms for free text queries only
rocchio_toggle = False # use rocchio algorithm for pseudo-relevance feedback
k = 50 # top k documents from initial set of retrieved results considered 'relevant' for pseudo-relevance feedback

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
        doc_lengths = pickle.load(dict) # key - doc_id, value - doc_length
        dictionary = pickle.load(dict) # key - token, value - (document frequency, pointer to postings)
        trimmed_documents = pickle.load(dict) # key - doc_id, value - list of 100 tokens with highest weighted tf.idf
        metadata = pickle.load(dict) # key - doc_id, value - [title, year, court]

    # print("size of trimmed documents[0]")
    # print(str(len(list(trimmed_documents.items())[0][1])))

    with open(queries_file, 'r') as query_file, open(results_file, 'w') as result_file:
        query_content = query_file.read().splitlines()

        # check for empty query
        if not query_content:
            print("no query found")  # for debugging
            result_file.write('\n')
            return

        query = query_content[0] # first line in query file is the query
        print("searching for : " + query) # for debugging

        # parse and evaluate query to obtain results
        parsed_query = parse_query(query)

        # check for free-text queries parsed, for deciding whether to perform query refinement
        # free text queries are those with only one inner list in parsed_query list and a single word in that inner list
        is_free_text_query = len(parsed_query) == 1 and " " not in parsed_query[0][0]

        # returned result will be ranked based on type of query:
        # free text query: ranked by cosine similarity score between query and set of documents in corpus
        # stand-alone phrasal query: ranked by tf of phrase
        # boolean query: ranked by cosine similarity of all tokens in query to set of retrieved documents

        if is_free_text_query and query_expansion_toggle:
            # perform query refinement using query expansion if it has been toggled
            # synonyms are found from Wordnet for nouns found in free text queries only

            print("performing query expansion with synonyms of nouns from Wordnet...")  # for debugging

            # expand query by adding noun synonyms of all nouns found in the query
            tokens = parsed_query[0]
            synonyms = expand_query(tokens)

            expanded_query = tokens + synonyms  # concatenate the two lists
            results = evaluate_query([expanded_query], dictionary, doc_lengths, postings_file)
            print("performed first round of retrieval.")  # for debugging
        else:
            results = evaluate_query(parsed_query, dictionary, doc_lengths, postings_file)
            print("performed first round of retrieval.")  # for debugging

        # perform query refinement using pseudo-relevance feedback (Rocchio algorithm) and query expansion
        # for free text queries only
        if is_free_text_query and rocchio_toggle:
            print("performing pseudo-relevance feedback with the Rocchio algorithm...")  # for debugging
            tokens = parsed_query[0] # 1d array of individual tokens from parsed_query

            query_vector = build_query_vector(tokens, dictionary, len(doc_lengths))
            # print("query vector in search.py")
            # print(list(query_vector.items())[:20])

            results = rocchio(query_vector, results[:k], dictionary, postings_file, doc_lengths, trimmed_documents)

        # order relevant documents by processing metadata
        # first rank by whether any part of the query is in the title, as this is the least important order
        # then by date, which are tiered based on how recent it is
        # lastly by court, as this is the primary/ overall order
        flattened_query = []
        for subquery in parsed_query:
            for token in subquery:
                if " " in token: # for phrases
                    split_phrase = token.split(" ")
                    for word in split_phrase:
                        flattened_query.append(word)
                else:
                    flattened_query.append(token)

        # print("preliminary results...")
        # print(results[:10])
        #
        # print("sorting results by metadata...")  # for debugging
        results = sort_results_by_metadata(results, metadata, flattened_query)
        # print(results[:10])

        print("retrieving " + str(len(results)) + " relevant results") # for debugging

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
