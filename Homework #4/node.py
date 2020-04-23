"""
A node in the postings list.
"""

class Node(object):
    def __init__(self, doc_id, ):
        self.doc_id = doc_id
        self.tf = 1 # first instance of term in doc, updated during indexing
        self.positions = [] # positional indices, updated during indexing
        self.nextNode = None # next node in order, updated during writing to disk
        self.skipNode = None # skip node, updated during writing to disk

    ### Term frequency operations ###
    def increment_tf(self):
        self.tf += 1

    def get_tf(self):
        return self.tf

    ### Positional index operations ###
    def add_position(self, index):
        self.positions.append(index)

    ### Node operations ###
    def set_next(self, node):
        self.nextNode = node

    def set_skip(self, node):
        self.skipNode = node

    def get_next(self):
        return self.nextNode

    def get_skip(self):
        if (self.has_skip):
            return self.skipNode

    def has_next(self):
        return self.nextNode != None and type(self.nextNode) == Node

    def has_skip(self):
        return self.skipNode != None and self.skipNode != self
