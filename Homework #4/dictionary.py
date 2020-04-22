import pickle

class Dictionary(object):
    def __init__(self, out_file):
        self.out_file = out_file
        self.terms = {} # key - term, value - [document_frequency, pointer_to_postings_list]
        self.doc_lengths = {} # only assigned during searching

    def get_terms(self):
        return self.terms

    def get_no_of_docs(self):
        return len(self.doc_lengths)

    def get_doc_length(self, key):
        return self.doc_lengths[key]

    def has_term(self, term):
        return term in self.terms

    def add_unique_term(self, term, pointer):
        """
        Adds a unique term to the dictionary with document frequency of 1 and a pointer to the term's entry in the
        postings list during indexing. Called during indexing.

        @param term the unique term to be added
        @parm pointer a pointer to the term in postings during indexing
        """
        self.terms[term] = [1, pointer]

    def increment_df(self, term):
        """
        Increments the document frequency of specified term by 1. Pre-condition: term already exists in the dictionary.

        @param term the existing term whose document frequency is to be incremented
        """
        self.terms[term][0] += 1

    def update_pointer(self, term, pointer):
        """
        Updates the given term with a pointer to its entry in the postings list saved on disk. Called at the end of
        indexing.

        @param term the existing term whose pointer is to be updated
        @param pointer the pointer to postings list saved on disk for the given term at the end of indexing
        """
        self.terms[term][1] = pointer

    def get_df(self, term):
        if self.has_term(term):
            return self.terms[term][0]
        else:
            return 0

    def get_pointer(self, term): # only called when the term exists in the dictionary
        if self.has_term(term):
            return self.terms[term][1]
        else:
            return None

    def save(self, doc_lengths):
        with open(self.out_file, 'wb') as dict:
            pickle.dump(doc_lengths, dict)
            pickle.dump(self.terms, dict)

    def load(self):
        with open(self.out_file, 'rb') as dict:
            self.doc_lengths = pickle.load(dict)
            self.terms = pickle.load(dict)
