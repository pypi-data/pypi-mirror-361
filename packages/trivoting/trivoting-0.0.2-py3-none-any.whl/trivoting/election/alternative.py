from __future__ import annotations

class Alternative:
    """
    Class representing an alternative, i.e., one of the potential outcome of the election.
    """

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        if isinstance(other, Alternative):
            return self.name == other.name
        elif isinstance(other, str):
            return self.name == other
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Alternative):
            return self.name < other.name
        elif isinstance(other, str):
            return self.name < other
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, Alternative):
            return self.name <= other.name
        elif isinstance(other, str):
            return self.name <= other
        return NotImplemented

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return self.__str__()
