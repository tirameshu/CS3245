def phrasal_query(phrase, postings):
    """
    assumes all postings of all files exist
    # postings:
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
    """
    [term1: {...}, term2: {...}, term3: {...}]
    """

    for term in phrase:
        if term in postings:
            phrase_postings.append(postings[term]) # returns a dictionary

    # compare 2-way at a time, only need to compare w the term before
    for i in range (1, len(phrase)):
        pass
