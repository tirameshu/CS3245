"""
A node in the postings list.
"""

class Node:
    def __init__(self, doc_id, pos):
        self.doc_id = doc_id
        self.positions = [pos] # positional indices, updated during indexing
        self.nextNode = None # next node in order, updated during writing to disk
        self.skipNode = None # skip node, updated during writing to disk

    ### Term frequency operations ###
    def get_tf(self):
        return len(self.positions)

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
