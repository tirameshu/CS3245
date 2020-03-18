This is the README file for A0180257E's submission

== Python Version ==

I'm using Python Version 3.7 for
this assignment.

== General Notes about this assignment ==

Indexing:
- after processing each word from each file into terms, each term is added to the dictionary
temporarily stored in `index.py`. Term frequency (term_freq) increments by 1 every time the same word
is encountered again in the same doc.
- the final dictionary format will be as follows:
dictionary = {term: {docID: [term_freq, weighted_term_freq, norm_w, df]}}
- idf is not required for document, but needed for query.
- weighted_term_freq is calculated at the end of each doc. In the same function, docLength is also calculated.
- normalised_weight (norm_w) is then calculated for each term, based on weighted_term_freq and docLength.
Document frequency (df) is added here as well, but directly to the dictionary `to_dict` that will be dumped into dictionary.txt.
-- to_dict will be in the following format:
to_dict = {term: [df, pointer_to_posting, pointer_to_champion]}
- the docs of top 10 norm_w of each term will be dumped in champion_list.txt to be used in searching.
(there may be > 10 docs for each term, because some docs might have same weight)
- dictionary is processed and re-formatted for each term, and all postings are dumped into postings.txt
- the docLength dictionary, together with to_dict, are dumped into dictionary.txt.

Searching:
- for every query term, top 10 of its posting is loaded from postings.txt --> dictionary re-constructed
but only for terms queried.
- df of query term can be obtained from (len(dictionary[term]))

== Files included with this submission ==

index.py:

search.py:

dictionary.txt:
- storage format:
docLength[N]
{term: [df, pointer_to_posting, pointer_to_champion]}

postings.txt:
[(docID1_1, term_freq1, norm_w1), (docID1_2, term_freq2, norm_w2),...]
[(docID2_1, term_freq1, norm_w1), (docID2_2, term_freq2, norm_w2),...]
...

champion_list.txt (only up to top 10 norm_w):
[(docID1_1, term_freq1, norm_w1), (docID1_2, term_freq2, norm_w2),...]
[(docID2_1, term_freq1, norm_w1), (docID2_2, term_freq2, norm_w2),...]

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I/We, A0180257E, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>
