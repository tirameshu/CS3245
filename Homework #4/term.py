"""
A term in the dictionary.
"""

class Term:
    def __init__(self, token, zone):
        self.token = token # the stemmed token associated with this term
        self.zone = zone # which zone of the document the term is found in

    def get_token(self):
        return self.token

    def get_zone(self):
        return self.zone
