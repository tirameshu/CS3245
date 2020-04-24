"""
A term in the dictionary saved on disk.
"""
class Term:
    def __init__(self, token, df, pointer):
        self.token = token # the stemmed token associated with this term
        self.df = df # document frequency of this term
        self.pointer = pointer # pointer to postings list on disk

    def get_token(self):
        return self.token

    def get_df(self):
        return self.df

    def get_pointr(self):
        return self.pointer