"""
A term in the dictionary.

On first encounter of a term, it will be initialised, then added to the dictionary in Index.

Upon further encounters of the same term, it will be updated via the dictionary in Index,
and if the term appears in more than 1 zone, the next zone will be added to self.zones.
"""
class Term:
    def __init__(self, token, zone):
        self.token = token # the stemmed token associated with this term
        # self.zones = [zone] # which zone of the document the term is found in.
        # TODO: @atharv we need to decide whr to put zone, determines methods to support
        self.df = 0
        self.pointer = 0

    def update_zones(self, zone):
        self.zones.append(zone)

    def increment_doc_freq(self):
        """
        When a term is encountered in another doc, increment df by 1
        :param df: doc_frequency of term
        :return: nil
        """
        self.df += 1

    def assign_pointer(self, pointer):
        self.pointer = pointer

    def get_token(self):
        return self.token

    def get_zones(self):
        return self.zones