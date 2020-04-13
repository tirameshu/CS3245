This is the README file for A0180257E's and A0158850X's submission
emails: e0273834@u.nus.edu and e0042053@u.nus.edu

== Python Version ==

We're using Python Version 3.7.4 for this assignment.

== General Notes about this assignment ==

1. For every search, delimit with AND op, and first retrieve for each query term separately.
A query term can be a phrase.

2. Weighted zone scoring is used. Even though each document has 5 fields, what is more significant is
the separation of metadata from the content body of the document, to facilitate searching of
documentID, date, court, etc., which are very likely to be queried specifically.
2.1 Therefore there are 2 zones for every document: metadata (zone1) and content (zone2).
2.2 The weight of zone1 is to be set higher than that of zone2, to facilitate specific searches
in fields. // TODO: decide on whether it shld rly be higher, and how much higher
2.3 If multiple query terms exist, they must be connected by AND, therefore weighted zone can be calculated
for each term and summed using the algorithm as described in Fig 6.4 of Textbook Chapter 6.
2.4 This implementation covers both the searching of query terms in fields and content body.

3. Query Refinement

== Work Allocation ==
Wang Xinman: drafted the structure of implementation, implementation of zones and fields

== Files included with this submission ==

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] We, A0180257E and A0158850X, certify that we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, we
expressly vow that we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.