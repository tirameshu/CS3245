zone_weights = []

def and_search(p1, p2):
    result = []
    i, j = 0, 0
    while i < len(p1) and j < len(p2):
        doc1 = p1[i]
        doc2 = p2[i]

        if doc1 == doc2:
            result.append(doc1)
        elif doc1 < doc2:
            i += 1
        else:
            j += 1

    return result

def calculate_g():
    return (n_10r + n_01n) / (n_10r + n_10n + n_01r + n_01n)


"""
:param node: contains docID, term, fields and corresponding boolean values
for whether it contains the term, etc
:param zone_weights: weights given to each zone to be multiplied with boolean
:return zone_score: sum of zone_score for each zone
"""
def get_weighted_zone(node, zone_weights): # TODO: @atharv, depends on your implementation
    """
    implementation 1: every zone contains a boolean value

    implementation 2: node has attributes "in_metadata" and "in_body",
    with boolean values for both, so calculation is only done based on these two.
    """
    pass

def get_consecutives(positions1, positions2):
    result = []
    i, j = 0, 0
    while i < len(positions1) and j < len(positions2):
        p1 = positions1[i]
        p2 = positions2[j]

        # p2 has to be after p1
        if p2 <= p1:
            j += 1
            continue

        elif p2 - p1 == 1:
            result.append((p1, p2))

            i += 1
            j += 1

        else:
            i += 1

    return result

"""
:param phrase: list of (processed) query terms
:param postings: dictionary of terms and their positions for each doc
:return result: list of docs containing the phrase
"""
def phrasal_query(phrase, postings):
    """
    postings:
    {
        term1: {
            doc1: [position1, position2, ...]
            doc2: [position1, position2, ...]
        }
        term 2: {
        ...
        }
        ...
    }

    2-way merge: take first 2 terms to look through positions first, then add another
    """

    # adding the docs and corresponding positions for all query terms
    # needs to be refreshed for every new query

    phrase_postings = []

    for term in phrase:
        if term in postings:
            phrase_postings.append(postings[term]) # returns a dictionary
        # TODO: If any of the query terms is not in postings, should we not return anything or still return based on whatever's left?

    if phrase_postings:
        result = phrase_postings[0]
        # compare 2-way at a time, only need to compare w the term before
        for i in range (1, len(phrase_postings)): # TODO assuming for now a normal case only
            term1_docs = result
            term2_docs = phrase_postings[i]

            # find intersection of docs
            shared_docs = set(term1_docs.keys()).intersection(set(term2_docs.keys()))

            temp = {} # after looking through docs containing the exact phrase

            for doc in shared_docs:
                p1 = term1_docs[doc]
                p2 = term2_docs[doc]

                temp[doc] = get_consecutives(p1, p2) # can be empty list, but maintain same format for future merging

            result = temp

        return result # dictionary of docs with a list of the positions of the last query term

    else: # if no term in phrase is in dictionary
        return []

"""
posting = {
    "term1": {
        1: [1, 2, 4, 5],
        2: [2, 6, 9]
    },

    "term2": {
        1: [1, 3, 6],
        2: [1, 6, 10]
    }
}
"""

"""
For query containing AND: we will first merge the posting lists of
all query terms, then conduct zone-scoring.

As such, regardless of boolean search or free text search or phrasal search,
zone-scoring only takes in 1 list of nodes, which is already the list of docIDs
to return to user.

This step is just to rank the docIDs. 

:param posting: posting list

:return scores: a dictionary of { docID: zone_score }
"""
def get_zone_score(posting):
    scores = {}
    for i in range (len(posting)):
        node = posting[i]
        scores[node.docID] = get_weighted_zone(node, zone_weights)

    return scores