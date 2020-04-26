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

1. Assumptions on entry of query by user
    1.1 Users will query title or content of a case, rather than court or date.
        1.1.1 Based on a preliminary lookup of dataset.csv, titles are included in the content. Hence, we assume this is
        true for the whole dataset and search only the content. However, we use metadata such as title, court, and year
        to re-rank the top decile of documents retrieved.
    1.2 User will enter queries in the appropriate format. However, the following provisions are made for improper query
    entry:
        1.2.1 If user enters a phrase beginning but not ending with quotation marks, e.g. ``"fertility treatment`, it is
        treated as a phrase.
        1.2.2 If user enters a mixture of phrasal and free text query,
            1.2.2.1 If the phrase appears first, e.g. ``"cat dog" lion`, then the whole query is treated as a phrasal
            query.
            1.2.2.2 If the free text appears first, e.g. `lion "cat dog"`, then a free text search is run with tokens
            `lion`, ``"cat`, and `dog"`, which may return undesirable results.
        1.2.3 If user enters a multi-word free text query in a boolean AND query, e.g. `cat dog AND lion`, then the
        query is treated as `cat AND dog AND lion`. Here, we run a boolean AND query on each token because we assume
        that since a user has opted for boolean AND search, they desire exact matches.
        1.2.4 If the user enters an incomplete boolean query, e.g. `cat AND `, we run a boolean search on the complete
        terms in the query i.e. on `cat`.

2. Query parsing
    2.1 Query is first delimited by `"AND"`.
    2.2 Phrases in the delimited query (entries containing " ") are tokenised, stemmed, and rejoined.
        2.2.1 For example, the phrase ``"fertility treatment"` is parsed as `"fertil treatment"`.
        2.2.2 Such parsing is consistent with the stemming performed during indexing, which ensures that the phrasal
        search is accurate.
        2.2.3 If the whole phrase was stemmed together, `"fertility treat"` would be obtained, which would result in
        imprecise retrieval.
    2.3 For multi-word free text queries, stop words are removed if the query contains at least one non-stopword.
        2.3.1 For instance, for the query `"the quiet phone call"`, "the" is removed, as the other words are not stop
        words.
        2.3.2 However, the query `"you are the"` is processed without stop word removal as we assume that returning no
        results is worse than returning results by running the supplied query as is.

3. Free text query search
    3.1 Implemented using the vector space model, where cosine similarity between query vector and document vector is
    determine using the lnc.ltc ranking scheme to rank relevant documents.
    3.2 Only documents with a cosine similarity score above a certain threshold are retrieved as relevant.
        3.2.2 This threshold is determined by finding the median for each percentile of the document scores in the
        vector space, and then averaging these median values.
        3.2.1 This threshold uses a less subjective statistical measure that yields a value that lies between the mean
        and the median of the document scores. The mean is not used as threshold as we found that it dramatically
        reduces recall, which we thought could reduce precision, while the median halves the recall without affecting
        precision too much.
        3.2.2 Hence, this method of finding the threshold seeks an intuitive balance between precision and recall.

4. Phrasal search
    4.1 Implemented using the positional intersect algorithm. Even though the phrasal queries are 2-3 words long, this
    algorithm works for n-word phrases.
    4.2 To improve speedup, we return an empty list whenever the intermediate results are empty.
    4.3 Unfortunately, we cannot guarantee that the documents returned have exact matches with the phrasal query,
        as the terms are stemmed during indexing.
    4.4 The relevant documents retrieved are further ranked based on the weighted term frequency of the phrase in each
    document.

5. Boolean search
    4.1 Implemented using the AND intersection algorithm. As we did not use skip pointers, we simply leverage on
    Python's `Set` collection to perform the list merging.
    4.2 To improve speedup, we return an empty list whenever the intermediate results are empty.
    4.3 For boolean queries with phrases, phrasal search is conducted on the phrase as previously explained, and the
    result is merged with postings of the other tokens in the query.
    4.4 The relevant documents retrieved are further ranked based on cosine similarity between query and document.
        4.4.1 Here, the query is a free text query consisting of individual tokens from the original query (any phrases
        are tokenised into words too). This is to differentiate documents based on tf.idf scores of the queried terms,
        assuming that a document which sees a higher frequency of even just one of the terms is more relevant.

6. Query refinement
    6.1 We explored two query refinement techniques - pseudo-relevance feedback using Rocchio algorithm an query
    expansion using synonyms from Wordnet. These techniques are further discussed in BONUS.docx.
    6.2 Both query refinement techniques were only attempted for free text queries, as we assumed that the user would
    appreciate documents with exact matches if they were using the phrasal or boolean search feature.
    6.3 The Rocchio algorithm was implemented as follows:
        6.3.1 Trimmed document vectors consisting of top 100 tokens with highest tf.idf scores for each document were
        saved to disk during indexing.
        6.3.2 The original query was shifted using the centroid of the documents retrieved after the initial round of
        retrieval. Alpha = 1 and Beta = 0.75, based on a heuristic found on the Stanford NLP guide.
        6.3.3 Cosine similarity scores were calculated between the new query and the trimmed document vectors.
        6.3.4 The resulting list is sorted by cosine scores and returned as the updated list of relevant documents.
    6.4 Query expansion was implemented as follows:
        6.4.1 Synonyms that are nouns for each noun in the free text query were added to the original query by
        retrieving the appropriate synonym sets and parts of speech tags.
        6.4.2 The expanded query was evaluated as per usual as a free text query search.
    6.5 After testing both refinement techniques, we decided to toggle them off because they yielded unreliable results.
    We would require more expert relevance assessments and further refinement of these techniques before we can be
    confident of toggling them on.

7. Ranking by metadata
    7.1 The top decile of retrieved documents are further ranked based on metadata.
    7.2 These top documents are sorted in the following order:
        7.2.1 If part of the query is in the title, then the document is ranked higher.
        7.2.2 Cases from a higher court are ranked earlier. The court tiers are based on the provided court hierarchy
        information.
        7.2.3 More recent cases are ranked higher than less recent cases, based on the year of the case.
    7.3 This metadata ranking preserves the original score ranking of the retrieved documents when there are ties by
    leveraging Python's built in stable-sort mechanism.

== Work Allocation ==
Both contributed more or less equally to the assignment as we discussed and debugged our code together via lengthy zoom
sessions. However, we primarily worked the following key features:
A0180257E - Pseudo-relevance feedback using Rocchio algorithm, ranking by metadata, positional intersect algorithm for
phrasal search, ranked boolean search.
A0158850X - Query expansion using synonyms from Wordnet, query parsing, free text query search with weighted tf.idf
vector space model, documentation (readme, bonus, code-level).

== Files included with this submission ==
1. index.py
2. search.py
3. dictionary.txt
4. postings.txt
5. indexing_utils.py
6. searching_utils.py
7. query_refinement.py
8. Notes about Court Hierarchy.txt
9. README.txt
10. Bonus.docx

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
5. The Stanford NLP guide for determining alpha and beta weight values for implementing the Rocchio algorithm.
Available - https://nlp.stanford.edu/IR-book/html/htmledition/the-rocchio71-algorithm-1.html
6. Stack overflow forums, which we referred for an assortment of doubts and workarounds.

== Acknowledgements ==
We'd like to thank:
1. Two friends from SoC who had taken this module in a previous semester, who shared with us their reasoning behind
their attempt at this assignment. This discussion helped us improve upon their implementation of query expansion.
2. A friend from law school who told us how she performs legal case retrieval, thus allowing us to refine our
ranking of results by considering metadata such as title, year, and court.
