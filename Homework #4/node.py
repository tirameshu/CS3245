"""
A node in the postings list written on disk.
"""

class Node:
    def __init__(self, doc_id, pos):
        self.doc_id = doc_id # doc_id corresponding to this node
        self.positions = [pos] # positional indices, updated during indexing
        self.next_node = None # next node in order, updated during writing to disk
        self.skip_node = None # skip node, updated during writing to disk

    ### Term frequency operations ###
    def get_tf(self):
        return len(self.positions)

    ### Positional index operations ###
    def add_position(self, index):
        self.positions.append(index)

    ### Metadata operations ###
    def get_doc_id(self):
        return self.doc_id

    ### Node operations ###
    def set_next(self, node):
        self.next_node = node

    def set_skip(self, node):
        self.skip_node = node

    def get_next(self):
        return self.next_node

    def get_skip(self):
        if (self.has_skip):
            return self.skip_node

    def has_next(self):
        return self.next_node != None and type(self.next_node) == Node

    def has_skip(self):
        return self.skip_node != None and self.skip_node != self
