This is the README file for A0180257E's submission

== Python Version ==

I'm using Python Version 3.7 for
this assignment.

== General Notes about this assignment ==

Indexing:
- after processing each word from each file into terms, each term is added to the
dictionary temporarily stored in `index.py`.
- the final dictionary format will be as follows:
dictionary = {term: {docID: [term_freq, weighted_term_freq, norm_w, df]}}
- term_freq increments by 1 every time the same word is encountered again in the same doc.
- idf is not required for document.
- weighted_term_freq is calculated at the end of each doc. In the same function,
docLength is also calculated.
- normalised_weight (norm_w) is then calculated for each term, based on weighted_term_freq and docLength.
df is added here as well.
- Only docs of top 10 norm_w of each term will be sent to postings.txt to be used in searching.
(this means there may be > 10 docs loaded from postings, because some docs might have same weight)
- dictionary is processed and re-formatted for each term, and dumped into postings.txt, together with
the docLength of each doc.

Searching:
- for every query term, top 10 of its posting is loaded from postings.txt --> dictionary re-constructed
but only for terms queried.
- df of query term can be obtained from (len(dictionary[term]))

== Files included with this submission ==

index.py:

search.py:

dictionary.txt:
- storage format:
{term: [df, pointer_to_posting]}

postings.txt:
[(docID1_1, term_freq1, norm_w1), (docID1_2, term_freq2, norm_w2),...]
[(docID2_1, term_freq1, norm_w1), (docID2_2, term_freq2, norm_w2),...]
...

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
