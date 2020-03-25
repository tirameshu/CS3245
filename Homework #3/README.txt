This is the README file for A0180257E's and A0158850X's submission
emails: e0273834@u.nus.edu and e0042053@u.nus.edu

== Python Version ==

We're using Python Version 3.7.4 for this assignment.

== General Notes about this assignment ==

1. We assume that the full path of directory of documents is specified as input argument -i while indexing

2. We implement a Vector Space Model using the lnc.ltc ranking scheme discussed in the lecture notes for Week 7, without
any additional optimisations such as champion lists or stopword removal.

3. For indexing, we largely build on the code used for Homework 2. After tokenising, stemming, and case folding, we
store the terms and their term frequency in a dictionary, while calculating the document length for every document and
storing these in a list. During indexing, the index is built in memory.

4. While saving the index to disk, we store the document frequency and pointer to postings list for each
term in dictionary.txt while a postings list of document IDs and term frequency corresponding to each term is saved to
postings.txt. Both dictionary and postings list are serialised prior to storage.

5. For query parsing during search, we tokenize the alpha-numeric terms in the query along with stemming and case
folding. Any punctuation in the query or other non-alpha-numeric symbols are disregarded.

6. For searching, the parsed query is first converted into a query vector containing query terms and normalised term
frequency. The cosine scores for each document are then calculated according to the lnc-ltc algorithm described in
class.

7. A heap is used to retrieve the top 10 most relevant documents according to their cosine score. If two documents have
the same cosine score, the document IDs are listed in increasing order.

8. In terms of work allocation, generally speaking, A0180257E implemented index.py and A0158850X implemented search.py.
A0180257E helped debug search.py and A0158850X did the README and method-level documentation. Both worked on testing the
accuracy of the code.

== Files included with this submission ==

1. index.py: script for indexing
2. search.py: script for searching
3. postings.txt: text file containing serialised postings lists
4. dictionary.txt: text file containing serialised dictionary
5. README.txt: text file information about the homework

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] We, A0180257E and A0158850X, certify that we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, we
expressly vow that we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

== References ==
1. CS3245 Week 7 lecture notes for understanding the lnc.ltc ranking scheme and the cosine score algorithm.
2. Heapq documentation for implementing the heap. URL: https://docs.python.org/2/library/heapq.html
