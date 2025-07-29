from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable, Collection

from trivoting.election.alternative import Alternative

class AbstractTrichotomousBallot(ABC):
    """
    Abstract class used for typing.
    """

    @property
    @abstractmethod
    def approved(self) -> Collection[Alternative]:
        pass

    @property
    @abstractmethod
    def disapproved(self) -> Collection[Alternative]:
        pass

class TrichotomousBallot(AbstractTrichotomousBallot):
    """
    Represents a trichotomous ballot, i.e., a ballot in which the voter classifies the alternatives between approved,
    disapproved and not seen/no opinion.
    """

    def __init__(self, *, approved: Iterable[Alternative] = None, disapproved: Iterable[Alternative] = None):
        if approved is None:
            self._approved = set()
        else:
            self._approved = set(approved)

        if disapproved is None:
            self._disapproved = set()
        else:
            self._disapproved = set(disapproved)

        AbstractTrichotomousBallot.__init__(self)

    @property
    def approved(self) -> set[Alternative]:
        return self._approved

    @approved.setter
    def approved(self, value: Iterable[Alternative]):
        self._approved = set(value)

    @property
    def disapproved(self) -> set[Alternative]:
        return self._disapproved

    @disapproved.setter
    def disapproved(self, value: Iterable[Alternative]):
        self._disapproved = set(value)

    def add_approved(self, alt: Alternative):
        self.approved.add(alt)

    def add_disapproved(self, alt: Alternative):
        self.disapproved.add(alt)

    def freeze(self):
        return FrozenTrichotomousBallot(
            approved=self.approved,
            disapproved=self.disapproved,
        )

    def __contains__(self, item):
        return item in self.approved or item in self.disapproved

    def __len__(self):
        return len(self.approved) + len(self.disapproved)

    def __str__(self):
        return f"{{{self.approved}}} // {{{self.disapproved}}}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, TrichotomousBallot):
            return self.approved == other.approved and self.disapproved == other.disapproved
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, TrichotomousBallot):
            return self.approved < other.approved
        return NotImplemented


class FrozenTrichotomousBallot(AbstractTrichotomousBallot):

    def __init__(self,  *, approved: Iterable[Alternative] = None, disapproved: Iterable[Alternative] = None):
        if approved is None:
            self._approved = tuple()
        else:
            self._approved = tuple(approved)

        if disapproved is None:
            self._disapproved = tuple()
        else:
            self._disapproved = tuple(disapproved)

        AbstractTrichotomousBallot.__init__(self)

    @property
    def approved(self) -> tuple[Alternative, ...]:
        return self._approved

    @property
    def disapproved(self) -> tuple[Alternative, ...]:
        return self._disapproved
