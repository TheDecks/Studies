import re


class Paragraph:

    def __init__(self, text: str):

        self.text = text

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text

    def find_proper_names_candidates(self):
        groups = re.findall(r'(?<!\.\s)(?<!")(?<![oO]f )(([A-Z][a-z]{2,}[ ]?)+)[,. ]', self.text)
        return [entry[0].strip().strip('.,') for entry in groups]
