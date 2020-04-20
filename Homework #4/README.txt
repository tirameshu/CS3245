This is the README file for A0180257E's and A0158850X's submission
emails: e0273834@u.nus.edu and e0042053@u.nus.edu

== Python Version ==

We're using Python Version 3.7.4 for this assignment.

== General Notes about this assignment ==

==== Index ===
1. We assume that the full path of directory of documents is specified as input argument -i while indexing

2. We index title, content, date and court as separate dictionaries, as each `in` search is O(1), so searching
with separate dictionaries is effectively O(1), rather than looping through all docs.

3. Posting: { Doc_Class: [list of positions] }

----------------

=== Search ===
1. Query Processing.
    1.1 For every search, delimit with AND op, and first retrieve for each query term separately.
        1.1.1 If there's no AND (ie result of delimitation is of length 1)
            1.1.1.1 If there is quotation mark, then it's phrasal search.
            1.1.1.2 Else, free text search. Conduct normal tf-idf scoring,
                    to be summed with weighted zone scoring, calculated for each individual query term.
        1.1.2 Else
            1.1.2.1 Merge the posting lists first.
            1.1.2.2 If the result of delimitation involves quotation marks, means the query involves a phrase.
                    Then conduct phrasal search, involving zones and fields.
            1.1.2.3 Else, free text search as above.

2. Zones and Fields.
    2.1 Weighted zone scoring is used for all searches: free-text, boolean and phrasal.
        2.1.1 Even though each document has 5 fields, what is more significant is
              the separation of metadata from the content body of the document,
              to facilitate searching of title, date, court, etc., which are very likely to be queried specifically.

    2.2 Therefore there are 2 zones for every document: metadata (zone1) and content (zone2).

    2.3 The weight of zone1 is to be set higher than that of zone2, to facilitate specific searches
        in fields. // TODO: decide on whether it shld rly be higher, and how much higher

    2.4 If multiple query terms exist, they must be connected by AND, therefore weighted zone can be calculated
        for each term and summed using the algorithm as described in Fig 6.4 of Textbook Chapter 6.

    2.5 This implementation covers both the searching of query terms in fields and content body.

3. Phrasal Search.
Potential edge cases:
1. Repeated words, eg "one by one"

4. Query Refinement

== Work Allocation ==
Wang Xinman: drafted the structure of implementation, implementation of zones and fields, and phrasal search

== Files included with this submission ==

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] We, A0180257E and A0158850X, certify that we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, we
expressly vow that we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.