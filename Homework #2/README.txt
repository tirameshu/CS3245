This is the README file for A0180257E's submission
e0273834@u.nus.edu

== Python Version ==

I'm using Python Version 3.7.3 for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

*Indexing*
- Stores a list of all file numbers at the first line, to facilitate searching with NOT operator.
- Loops through all files, and processes each word into a term.
- Each file number (docID) is also converted into a Node.
- Each term is then stored into dictionary in script, where each term corresponds
 to a list of nodes. (As stated in lines 80 - 85 of index.py)
- All postings are subsequently sorted by docID, and skip pointers are added to nodes.
 At the same time, node.next is also set up to facilitate skipping.
- Finally, postings are dumped into postings.txt, and dictionary.txt is populated in the format:
 term doc_freq pointer_to_posting

*Searching*
- For every line of query, all query terms (excluding logical operators such as AND and brackets)
 are processed into terms. This is so that for each line of query, the dictionary file is only looped
 through once to obtain postings for all the query terms.
- Subsequently, each query term is pushed into a stack.
- As brackets take priority, those inside brackets are pushed into a separate stack to be searched for
 and merged immediately, via "simple merge". After which, the resulting list of nodes is pushed back into the original stack.
- After all brackets are taken care of, the resultant "linear" query is subsequently passed into "simple merge".
 This separate function allows the same code to be reused, also helping with clarity.
- Inside simple merge, NOT operations take top priority, and are thus processed first. Again, result is pushed back into stack.
-- For not_search, the corresponding list of nodes for the term is first sought. Subsequently, it is "minus-ed" from the list
 of all files. New nodes have to be created, and skip pointers were again implemented to facilitate potential future and_merge.
- After NOT, AND is processed. It is assumed that both lists are already sorted, since they are taken directly from the dictionary.
-- Inside and_merge, the heuristics mentioned during lecture is implemented. As the posting lists consist of nodes, we first check
 if the node is allocated a skip pointer. The first node always has a skip pointer, so the smaller node compares its skip pointer
 value against the other node. If the skip pointer is still smaller, it can safely skip over. This continues until both nodes
 have the same value, following which the node is appended to the result list, and both nodes advance to the next one.
- After AND, OR is processed. It is assumed that both lists are already sorted, since they are taken directly from the dictionary.
-- Inside or_merge, the smaller node of the two lists are added to the result first, and the smaller node advances.
 This prevents duplicates.
- Final combined result is written to file.


== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

index.py: algo for indexing
search.py: algo for searching
dictionary.txt: list of terms, their doc_freq, and pointer to posting
postings.txt: list of documents containing the term that the line is being pointed to

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I/We, A0180257E, certify that I have followed the CS 3245 Information
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
