This is the README file for A0180257E's and A0158850X's submission
emails: e0273834@u.nus.edu and e0042053@u.nus.edu

== Python Version ==

We're using Python Version 3.7.4 for this assignment.

== General Notes about this assignment ==

==== Index ===
1. We assume that the full path of directory of documents is specified as input argument -i while indexing

2. We index title, content and court as separate dictionaries, as each `in` search is O(1), so searching
with separate dictionaries is effectively O(1), rather than looping through all docs.

3. We parse one doc at a time (one row of the csv file at a time), extracting the relevant zones that we intend to store.
    3.1 `collect_tokens` is first called to tokenise and stem the terms in the document.
    3.2 `process_tokens` is then called to capture the term_frequency (tf) of each term in the current document,
        and tf is stored in a separate dictionary `term_frequencies`, in the format of
        { (str) token: (int) docID: (Node) node }, where the node will store a list of positions of the token in the document.
    3.3 Then we store the information of zones `title` and `court` in separate dictionaries.

4. We then write the index dictionary to disc.
    4.1 We start by extracting all the nodes (containing docID and positions of the token in the doc),
        then updating their skip pointers and adjacent node.
    4.2 We then create a Term for each token, and assign it the corresponding document frequency (df) and
        pointer to its posting.
    4.3 All the indexing information is thus stored as:
        { Term1: [ Node1, Node2, ...]
          Term2: [ Node1, Node2, ...]
          ...
        } with `Term`s in dictionary.txt and `Node`s in postings.txt

----------------

=== Search ===

Assumption:
1. Users will query title or body, rather than court or date.
    1.1 However, court and date are important for relevance ranking.
2. Titles, courts and some dates are in the content, therefore it is safe to
    search through content first, then check if any of the docs (alr deemed relevant
    based on cosine similarity) has query in its title.
    2.1 Takes care of situations where say a date appears multiple times in one case but is
        the actual publishing date of another case.

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

== References ==
Introduction to Information Retrieval Textbook Chapter 6 p3-7 for zone scoring algorithm and understanding,
as well as formula for the optimal value of `g`.