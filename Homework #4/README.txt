This is the README file for A0180257E's and A0158850X's submission
emails: e0273834@u.nus.edu and e0042053@u.nus.edu

== Python Version ==

We're using Python Version 3.7.4 for this assignment.

== General Notes about this assignment ==

=== Indexing ===
1. Reading dataset csv file
    1.1 We assume that the first line of the dataset csv file contains fieldnames.
    1.2 Any encoding errors encountered while reading unmappable characters are ignored.

2. Indexing content of documents
    2.1 Tokens are collected from the content by `collect_tokens` in `indexing_utils.py`.
        2.1.1 Only alphanumeric tokens are collected.
        2.1.2 Tokens are stemmed using Porter Stemmer.
    2.2 Index is built by `process_tokens` in `indexing_utils.py`.
        2.2.1 Positional indices of tokens are stored in the index to facilitate phrasal search.
        2.2.2 Term frequencies of tokens in each document are stored for storing document lengths and document vector.

3. Indexing metadata of documents
    3.1 Title, year, and court of each case is extracted and stored to facilitate zone scoring

4. Writing dictionary and postings to disk
    4.1 Done by `write_to_disk` in `indexing_utils.py`.
    4.2 Information of the positions a certain token appears in a certain document is written to postings.txt.
    4.3 Information of the document frequency and pointer to postings list for each token is written to dictionary.txt.
    4.4 Information of document lengths, a trimmed document vector, and metadata is written to dictionary.txt.
        4.4.1 The trimmed document vector contains top 100 tokens with highest weighted tf.idf score in each document.
        This vector will be used for psuedo-relevance feedback using Rocchio algorithm during search.
    4.5 All data is serialised using Pickle before being written to disk.

5. We initially implemented a Node class to facilitate skip pointers during boolean AND search. However, serialising
these custom objects to disk resulted in a segmentation fault. Hence, we chose not to implement skip pointers for the
assignment.

=== Searching ===

1. List of key assumptions

1. Users will query title or body, rather than court or date.
    1.1 However, court and date are important for relevance ranking.
2. Titles, courts and some dates are in the content, therefore it is safe to
    search through content first, then check if any of the docs (alr deemed relevant
    based on cosine similarity) has query in its title.
    2.1 Takes care of situations where say a date appears multiple times in one case but is
        the actual publishing date of another case.
3. User will enter phrasal queries appropriately, ie a phrase enclosed on both ends with quotation marks.
    3.1 As such, as long as a query begins with a quotation mark, we will treat the subquery as a phrase.
4. "Correction" for user mistake
    4.1 If the query is `cat AND `, we take it as that the user has made a mistake, and that at least the
        first term is still relevant to what the user is searching for, thus still returning relevant documents
        based on that.

1. Query Processing.
    1.1 For every search, delimit with AND op, and first retrieve for each query term separately.
        1.1.1 If there's no AND (ie result of delimitation is of length 1)
            1.1.1.1 If there is quotation mark, then it's phrasal search.
            1.1.1.2 Else, free text search. Conduct normal tf-idf scoring,
                    to be summed with weighted zone scoring, calculated for each individual query term.
        1.1.2 Else
            1.1.2.1 Call the first search function on the two components.
            1.1.2.2 If the result of delimitation involves quotation marks, means the query involves a phrase.
                    Then conduct phrasal search, involving zones and fields.
            1.1.2.3 Else, free text search as above.

2. Zones and Fields.
    2.1 We will search through the content of the document first, then sort the resulting documents
        by their metadata.

    2.2 To facilitate searches specific to any of the metadata, especially `title`, we will rank the documents
        by existence in metadata first (specifically, title), followed by date (for every decade later than the
        current year, the relevance drops proportionally), and then court (higher court -> higher weight).
        2.2.1 As the weights are varied within each zone, this is not really weighted-zone score.
        TODO: proportional for year?

3. Phrasal Search.
    3.1 Query phrase is first tokenised into words, and the posting of each word is found separately.

    3.2 Then find intersection of the postings based on the docIDs, same as boolean search.
        3.2.1 However, the list of positions for each query term is kept separate.
        3.2.2. The lists of positions should be ordered according to the order of the words in the phrase.

    3.3 Loop through the nodes in the resultant list, and check whether the positions of the words in the phrase
        are in the desired order.
        3.3.1 Also note the number of times the phrase appeared in the document and use the same df formula for it,
                while also normalising by document length.

    3.4 Potential edge cases:
        3.4.1. Repeated words, eg "one by one", "so so"

    3.5 Unfortunately we cannot guarantee that the documents returned have exact matches with the phrasal query,
        as the terms are stemmed.

4. Boolean Query
    4.1 Every component of a boolean query is interpreted as joined by AND, eg cat mouse AND dog == cat AND mouse AND dog,
        thus the posting for each term in the query is found and intersected.
    4.2 For boolean queries with phrases, phrasal query is conducted on the phrase, and resulting posting list is
        similarly intersected with the other parts of the boolean query.
    4.3 Ranking of the intersected documents is determined by cosine similarity between query and document, where
        the query now is taken to be free text. This is to differentiate documents based on frequencies
        of the queried terms, assuming that a document which sees a higher frequency of even just one of the terms
        is more likely to be relevant.

5. Ranking
    5.1 For boolean queries, we are ranking the results by scoring documents based on the tf of the tokens in the query
        in the documents, then normalising by document length.
        5.1.1 We are not using log as it is an increasing function anyway, so a document with a higher absolute tf
              for a token will also have a higher log value.


== Work Allocation ==
Both contributed more or less equally to the assignment as we discussed and debugged our code together via lengthy zoom
sessions. However, we primarily worked the following key features:
A0180257E - Pseudo-relevance feedback using Rocchio algorithm, ranking by metadata, positional intersect algorithm for
phrasal search, ranked boolean search.
A0158850X - Query expansion using synonyms from Wordnet, query parsing, free text query search with weighted tf.idf
vector space model, documentation (readme, bonus, code-level).

== Files included with this submission ==

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] We, A0180257E and A0158850X, certify that we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, we
expressly vow that we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.

== References ==
1. Introduction to Information Retrieval Textbook Chapter 9 p162-172 for understanding relevance feedback and query
expansion.
2. A video on a worked example involving the Rocchio algorithm helped us implement it for query refinement. The video is
available here: https://www.coursera.org/lecture/text-retrieval/lesson-5-2-feedback-in-vector-space-model-rocchio-PyTkW
3. The WordNet interface. Available - https://www.nltk.org/howto/wordnet.html
4. A discussion on ResearchGate for determining a suitable threshold for cosine similarity. We did not directly use any
implementation discussed here, but this helped us think about more objective ways to determine a threshold.
Available - https://www.researchgate.net/post/Determination_of_threshold_for_cosine_similarity_score
5. Stack overflow forums, which we referred for an assortment of doubts and workarounds.

== Acknowledgements ==
We'd like to thank:
1. Two friends from SoC who had taken this module in a previous semester, who shared with us their reasoning behind
their attempt at this assginment. This discussion helped us improve upon their implementation of query expansion.
2. A friend from law school who told us how she performs legal case retrieval, thus allowing us to refine our
ranking of results by considering metadata such as title, year, and court.
