from collections.abc import Iterable

from trivoting.election.alternative import Alternative


class Selection:
    def __init__(self, selected: Iterable[Alternative] = None, rejected: Iterable[Alternative] = None, implicit_reject: bool = True):
        if selected is None:
            self.selected = list()
        else:
            self.selected = list(selected)
        if rejected is None:
            self.rejected = list()
        else:
            self.rejected = list(rejected)
        self.implicit_reject = implicit_reject

    def is_selected(self, a: Alternative):
        if self.implicit_reject:
            return a not in self.selected
        return a in self.rejected

    def add_selected(self, alt: Alternative):
        self.selected.append(alt)

    def extend_selected(self, alts: Iterable[Alternative]):
        self.selected.extend(alts)

    def add_rejected(self, alt: Alternative):
        self.rejected.append(alt)

    def extend_rejected(self, alts: Iterable[Alternative]):
        self.rejected.extend(alts)

    def sort(self):
        self.selected.sort()
        self.rejected.sort()

    def copy(self):
        return Selection(self.selected, self.rejected, self.implicit_reject)

    def __contains__(self, item):
        return item in self.selected or item in self.rejected

    def __len__(self):
        return len(self.selected)

    def total_len(self):
        return len(self.selected) + len(self.rejected)

    def __str__(self):
        return f"{{{self.selected}}} // {{{self.rejected}}}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, Selection):
            return self.selected == other.selected and self.rejected == other.rejected
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Selection):
            return self.selected < other.selected
        return NotImplemented

