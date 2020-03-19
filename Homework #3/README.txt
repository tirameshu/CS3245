This is the README file for A0180257E's submission

== Python Version ==

I'm using Python Version 3.7 for
this assignment.

== General Notes about this assignment ==

Assumptions:
1) nltk is in same directory as script

Active Decisions:
- to not use champion list as it is pointless; final score for any document does not depend on whether the document
has a higher weight for any individual term, but a number of them. A document containing more query terms
but small weights for them might have higher score than a document with high weights for only a few terms.
Tldr cannot determine, must calculate and then rank.
- to not only consider posting with > k number of query terms: need do stopword removal for query, merging takes time,
and involves going through all the postings anyway, might as well just calculate directly. Also hard to implement.

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
to_dict = {term: [df, pointer_to_posting]}
- dictionary is processed and re-formatted for each term, and all postings are dumped into postings.txt as a list of tuples,
as illustrated below, where each tuple consists of docID and norm_w.
- the docLength dictionary, together with to_dict, are dumped into dictionary.txt.

Searching:
- for every query term, its posting is first fetched, then its w_tq is calculated, and normalised by the length of the
weighted query vector.
- the product between w_tq and norm_w is then found for all query terms and added to score[d].

score_calc:
{term1:
    {docID1: [w_tq1_1, norm_w1_1]
     docID2: [w_tq1_2, norm_w1_2]
     ...
    }
...
}

scores:
{docID1: score1
...
}

== Files included with this submission ==

index.py:

search.py:

dictionary.txt:
- storage format:
docLength[N]
{
term1: [df1, pointer_to_posting1]
term2: [df2, pointer_to_posting2]
...
}

postings.txt:
[(docID1_1, norm_w1), (docID1_2, norm_w2),...]
[(docID2_1, norm_w1), (docID2_2, norm_w2),...]
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
