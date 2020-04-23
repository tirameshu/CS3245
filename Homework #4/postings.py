import pickle

class Postings:
    def __init__(self, out_file):
        self.out_file = out_file
        self.postings = [] # [{document_ID: term_frequency}]

    def get_length(self):
        return len(self.postings)

    def add_entry(self, doc_id):
        """
        Creates a new entry in postings only when a unique token is encountered during indexing.
        """
        self.postings.append({doc_id: 1}) # set term frequency to 1

    def has_doc_id(self, doc_id, index):
        """
        Returns true if given doc_id is present in postings list of the term corresponding to the given index.

        @param doc_id integer corresponding to document_ID to be found in postings
        @param index index corresponding to the term for which the document_ID is to be checked
        """
        return doc_id in self.postings[index]

    def update_entry(self, doc_id, index):
        """
        Updates entry in postings list for the term corresponding to the specified index.

        If the specified doc_id already exists in the term's postings list, the term frequency is incremented, otherwise
        the doc_id is added to the term's postings list.

        @param doc_id an integer document_ID to be updated in postings
        @param index the index in postings at which the doc_id is to be updated
        @return true if document frequency of term increases, that i, if doc_id is added to postings, false otherwise
        """
        if self.has_doc_id(doc_id, index):
            self.postings[index][doc_id] +=1
            return False
        else:
            self.postings[index][doc_id] = 1
            return True

    def save(self, dictionary):
        with open(self.out_file, 'wb') as post:
            for term in dictionary.get_terms():
                index = dictionary.get_pointer(term)
                postings_list = sorted(self.postings[index].items()) # sort by doc_id

                dictionary.update_pointer(term, post.tell())

                pickle.dump(postings_list, post)

    def load(self, offset):
        """
        Loads postings list at specified offset. Pre-condition: the term whose posting is to be loaded must already
        exist in the dictionary.

        @param offset the offset at which the postings list is loaded from disk
        """
        with open(self.out_file, 'rb') as post:
            post.seek(offset)
            postings_list = pickle.load(post)
            post.seek(0) # rewind
            return postings_list
