from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter, defaultdict
from collections.abc import Iterable, MutableSequence, MutableMapping, Iterator
from itertools import product

from trivoting.election.alternative import Alternative
from trivoting.election.trichotomous_ballot import TrichotomousBallot, AbstractTrichotomousBallot, \
    FrozenTrichotomousBallot
from trivoting.fractions import Numeric
from trivoting.rules.selection import Selection
from trivoting.utils import generate_subsets, generate_two_list_partitions


class AbstractTrichotomousProfile(ABC, Iterable[AbstractTrichotomousBallot]):
    """
    Abstract class representing a profile, that is, a collection of ballots. This class is only meant to be inherited.

    """

    def __init__(self, alternatives: Iterable[Alternative] = None, max_size_selection : int = None):
        if alternatives is None:
            self.alternatives = set()
        else:
            self.alternatives = set(alternatives)
        self.max_size_selection = max_size_selection

    @abstractmethod
    def multiplicity(self, ballot: AbstractTrichotomousBallot) -> int:
        """
        Returns the multiplicity of a ballot.

        Parameters
        ----------
            ballot : AbstractTrichotomousBallot
                The ballot whose multiplicity is inquired.

        Returns
        -------
            int
                The multiplicity of the ballots.
        """

    @abstractmethod
    def num_ballots(self) -> int:
        """
        Returns the number of ballots in the profile.

        Returns
        -------
            int
                The multiplicity of the ballots.
        """

    @abstractmethod
    def add_ballot(self, ballot: AbstractTrichotomousBallot):
        """
        Adds a ballot to the profile.

        Parameters
        ----------
            ballot : AbstractTrichotomousBallot
                The ballot to add.
        """

    def add_ballots(self, ballots: Iterable[AbstractTrichotomousBallot]):
        """
        Adds multiple ballots to the profile.

        Parameters
        ----------
            ballots : Iterable[AbstractTrichotomousBallot]
                The ballots to add.
        """
        for ballot in ballots:
            self.add_ballot(ballot)

    @abstractmethod
    def support(self, alternative: Alternative) -> Numeric:
        """
        Returns the support of an alternative, i.e., the net number of voters supporting it (the number of approvers
        minus the number of disapprovers).
        
        Parameters
        ----------
            alternative: Alternative
                The alternative to consider.

        Returns
        -------
            int
                The support of the alternative.
        """

    @abstractmethod
    def support_dict(self) -> defaultdict[Alternative, int]:
        """
        Returns the support of the alternatives of the instance as a dictionary. Alternatives not appearing in
        any ballot will not be present in the dictionary. The method returns a defaultdict so querying it for
        absent alternatives will succeed and return 0.

        Returns
        -------
            collections.defaultdict[Alternative, int]
                The support of each alternative appearing in at least one ballot.
        """
        
    @abstractmethod
    def approval_score(self, alternative: Alternative) -> int:
        """
        Returns the approval score of an alternative, i.e., the number of voters approving of it.
        
        Parameters
        ----------
            alternative: Alternative
                The alternative to consider.

        Returns
        -------
            int
                The approval score of the alternative.
        """

    @abstractmethod
    def approval_score_dict(self) -> defaultdict[Alternative, int]:
        """
        Returns the approval scores of the alternatives of the profile as a dictionary. Never approved alternatives
        will not be present in the dictionary. The method returns a defaultdict so querying it for
        non-approved alternatives will succeed and return 0.

        Returns
        -------
            collections.defaultdict[Alternative, int]
                The approval score of each alternative appearing in at least one ballot.
        """
        

    @abstractmethod
    def disapproval_score(self, alternative: Alternative) -> int:
        """
        Returns the disapproval score of an alternative, i.e., the number of voters disapproving of it.
        
        Parameters
        ----------
            alternative: Alternative
                The alternative to consider.

        Returns
        -------
            int
                The disapproval score of the alternative.
        """
       

    @abstractmethod
    def disapproval_score_dict(self) -> defaultdict[Alternative, int]:
        """
        Returns the disapproval scores of the alternatives of the profile as a dictionary. Never disapproved alternatives
        will not be present in the dictionary. The method returns a defaultdict so querying it for
        non-approved alternatives will succeed and return 0.

        Returns
        -------
            collections.defaultdict[Alternative, int]
                The disapproval score of each alternative appearing in at least one ballot.
        """

    @abstractmethod
    def approval_disapproval_score(self, alternative: Alternative) -> tuple[int, int]:
        """
        Returns the approval and disapproval score of an alternative together at the same time.
        
        Parameters
        ----------
            alternative: Alternative
                The alternative to consider.

        Returns
        -------
            tuple[int, int]
                The approval and the disapproval score of the alternative.
        """
       

    @abstractmethod
    def approval_disapproval_score_dict(self) -> tuple[defaultdict[Alternative, int], defaultdict[Alternative, int]]:
        """
        Returns the dictionaries of the approval score and of the disapproval score.

        Returns
        -------
            tuple[collections.defaultdict[Alternative, int], collections.defaultdict[Alternative, int]]
                The approval score and the disapproval score dictionaries.
        """

    def all_feasible_selections(self, max_size_selection: int) -> Iterator[Selection]:
        """
        Returns an iterator that yields all feasible (partial) selections.

        Parameters
        ----------
            max_size_selection: int
                Maximum number of alternatives that can be selected in a selection.

        Returns
        -------
            Iterator[Selection]
                An iterator that yields all feasible (partial) selections.

        """
        for l1, l2 in generate_two_list_partitions(self.alternatives, first_list_max_size=max_size_selection):
            yield Selection(selected=l1, rejected=l2, implicit_reject=False)

    @abstractmethod
    def all_sub_profiles(self) -> Iterator[AbstractTrichotomousProfile]:
        """
        Returns an iterator that yields all possible subprofiles of the profile.

        Returns
        -------
            Iterator[AbstractTrichotomousProfile]
                An iterator that yields all possible subprofiles of the profile.

        """

class TrichotomousProfile(AbstractTrichotomousProfile, MutableSequence[TrichotomousBallot]):
    """
    Represents a trichotomous profile, i.e., a collection of trichotomous ballots, one per voter.

    Parameters
    ----------
        init: Iterable[TrichotomousBallot], Optional
            An iterable of trichotomours ballots used to initialise the profile.
        alternatives: Iterable[Alternative], Optional
            An iterable of alternatives representing all the alternatives of the instance.
        max_size_selection: int, Optional
            The maximum number of alternatives to be selected when computing the outcome of a rule on the profile.
            Used notably when reading files from preference libraries.

    Attributes
    ----------
        alternatives: set[Alternative]
            A set of alternatives representing all the alternatives of the instance.
        max_size_selection: int
            The maximum number of alternatives to be selected when computing the outcome of a rule on the profile.
            Used notably when reading files from preference libraries.
    """

    def __init__(
        self,
        init: Iterable[TrichotomousBallot] = (),
        *,
        alternatives: Iterable[Alternative] = None,
        max_size_selection: int = None,
    ) -> None:
        self._ballots_list = list(init)
        if alternatives is None and isinstance(init, AbstractTrichotomousProfile):
            alternatives = init.alternatives
        if max_size_selection is None and isinstance(init, AbstractTrichotomousProfile):
            max_size_selection = init.max_size_selection
        AbstractTrichotomousProfile.__init__(self, alternatives, max_size_selection)

    def support(self, alternative: Alternative) -> int:
        score = 0
        for ballot in self:
            if alternative in ballot.approved:
                score += 1
            elif alternative in ballot.disapproved:
                score -= 1
        return score

    def support_dict(self) -> dict[Alternative, int]:
        res = defaultdict(int)
        for ballot in self:
            for alt in ballot.approved:
                res[alt] += 1
            for alt in ballot.disapproved:
                res[alt] -= 1
        return res

    def approval_score(self, alternative: Alternative) -> int:
        score = 0
        for ballot in self:
            if alternative in ballot.approved:
                score += 1
        return score

    def approval_score_dict(self) -> dict[Alternative, int]:
        res = defaultdict(int)
        for ballot in self:
            for alt in ballot.approved:
                res[alt] += 1
        return res

    def disapproval_score(self, alternative: Alternative) -> int:
        score = 0
        for ballot in self:
            if alternative in ballot.disapproved:
                score += 1
        return score

    def disapproval_score_dict(self) -> dict[Alternative, int]:
        res = defaultdict(int)
        for ballot in self:
            for alt in ballot.disapproved:
                res[alt] += 1
        return res

    def approval_disapproval_score(self, alternative: Alternative) -> tuple[int, int]:
        app_score = 0
        disapp_score = 0
        for ballot in self:
            if alternative in ballot.approved:
                app_score += 1
            if alternative in ballot.disapproved:
                disapp_score += 1
        return app_score, disapp_score

    def approval_disapproval_score_dict(self) -> tuple[dict[Alternative, int], dict[Alternative, int]]:
        app_scores = defaultdict(int)
        disapp_scores = defaultdict(int)
        for ballot in self:
            for alt in ballot.approved:
                app_scores[alt] += 1
            for alt in ballot.disapproved:
                disapp_scores[alt] += 1
        return app_scores, disapp_scores

    def num_ballots(self) -> int:
        return len(self)

    def add_ballot(self, ballot: TrichotomousBallot):
        self.append(ballot)

    def multiplicity(self, ballot: TrichotomousBallot) -> int:
        """
        Returns 1 regardless of the input; even if the ballot does not appear in the profile (to save up computation).

        Parameters
        ----------
            ballot : TrichotomousBallot
                The ballot whose multiplicity is inquired.

        Returns
        -------
            int
                1
        """
        return 1

    def as_multiprofile(self) -> TrichotomousMultiProfile:
        """
        Returns the multiprofile corresponding to this profile. Ballots are frozen to make them unmutable.

        Returns
        -------
            TrichotomousMultiProfile
                The multiprofile.
        """
        return TrichotomousMultiProfile([ballot.freeze() for ballot in self], alternatives=self.alternatives, max_size_selection=self.max_size_selection)

    def all_sub_profiles(self) -> Iterator[TrichotomousProfile]:
        """
        Returns an iterator that yields all possible sub-profiles.

        Returns
        -------
            Iterator[TrichotomousProfile]
                An iterator that yields all possible sub-profiles.

        """
        for subset in generate_subsets(self._ballots_list):
            yield TrichotomousProfile(subset, alternatives=self.alternatives, max_size_selection=self.max_size_selection)

    def __getitem__(self, index):
        if isinstance(index, slice):
            new_obj = TrichotomousProfile(self)
            new_obj._ballots_list = self._ballots_list[index]
            return new_obj
        return self._ballots_list[index]

    def __setitem__(self, index, value):
        self._ballots_list[index] = value

    def __delitem__(self, index):
        del self._ballots_list[index]

    def __len__(self):
        return len(self._ballots_list)

    def __iter__(self):
        return iter(self._ballots_list)

    def __contains__(self, item):
        return item in self._ballots_list

    def __reversed__(self):
        return reversed(self._ballots_list)

    def append(self, value):
        self._ballots_list.append(value)

    def extend(self, iterable):
        self._ballots_list.extend(iterable)

    def insert(self, index, value):
        self._ballots_list.insert(index, value)

    def remove(self, value):
        self._ballots_list.remove(value)

    def pop(self, index=-1):
        return self._ballots_list.pop(index)

    def clear(self):
        self._ballots_list.clear()

    def index(self, value, start=0, end=None):
        if end is None:
            end = len(self._ballots_list)
        return self._ballots_list.index(value, start, end)

    def count(self, value):
        return self._ballots_list.count(value)

    def sort(self, *, key=None, reverse=False):
        self._ballots_list.sort(key=key, reverse=reverse)

    def reverse(self):
        self._ballots_list.reverse()

    def copy(self):
        return TrichotomousProfile(self)

    def __add__(self, other):
        new_profile = TrichotomousProfile(self)
        if isinstance(other, TrichotomousProfile):
            new_profile._ballots_list += other._ballots_list
        else:
            new_profile._ballots_list += other
        return new_profile

    def __iadd__(self, other):
        if isinstance(other, TrichotomousProfile):
            self._ballots_list += other._ballots_list
        else:
            self._ballots_list += other
        return self

    def __mul__(self, n):
        if not isinstance(n, int):
            return ValueError("Cannot multiply profiles with non-int.")
        new_profile = TrichotomousProfile(self)
        new_profile._ballots_list *= n
        return new_profile

    def __imul__(self, n):
        if not isinstance(n, int):
            return ValueError("Cannot multiply profiles with non-int.")
        self._ballots_list *= n
        return self

    def __repr__(self):
        return self._ballots_list.__repr__()

    def __str__(self):
        return self._ballots_list.__str__()


class TrichotomousMultiProfile(AbstractTrichotomousProfile, MutableMapping[FrozenTrichotomousBallot, int]):
    """
    Represents a trichotomous multi-profile, i.e., a collection of trichotomous ballots in which identical ballots
    are stored one together with their multiplicity.
    """

    def __init__(
        self,
        init: Iterable[FrozenTrichotomousBallot] = (),
        *,
        alternatives: Iterable[Alternative] = None,
        max_size_selection: int = None,
    ) -> None:
        self._ballots_counter = Counter(init)
        if alternatives is None and isinstance(init, AbstractTrichotomousProfile):
            alternatives = init.alternatives
        if max_size_selection is None and isinstance(init, AbstractTrichotomousProfile):
            max_size_selection = init.max_size_selection
        AbstractTrichotomousProfile.__init__(self, alternatives, max_size_selection)

    def support(self, alternative: Alternative) -> int:
        score = 0
        for ballot, count in self.items():
            if alternative in ballot.approved:
                score += count
            elif alternative in ballot.disapproved:
                score -= count
        return score

    def support_dict(self) -> dict[Alternative, int]:
        res = dict()
        for ballot, count in self.items():
            for alt in ballot.approved:
                if alt in res:
                    res[alt] += count
                else:
                    res[alt] = count
            for alt in ballot.disapproved:
                if alt in res:
                    res[alt] -= count
                else:
                    res[alt] = -count
        return res

    def approval_score(self, alternative: Alternative) -> int:
        score = 0
        for ballot, count in self.items():
            if alternative in ballot.approved:
                score += count
        return score

    def approval_score_dict(self) -> dict[Alternative, int]:
        res = defaultdict(int)
        for ballot, count in self.items():
            for alt in ballot.approved:
                res[alt] += count
        return res
    def disapproval_score(self, alternative: Alternative) -> int:
        score = 0
        for ballot, count in self.items():
            if alternative in ballot.disapproved:
                score += count
        return score

    def disapproval_score_dict(self) -> dict[Alternative, int]:
        res = defaultdict(int)
        for ballot, count in self.items():
            for alt in ballot.disapproved:
                res[alt] += count
        return res

    def approval_disapproval_score(self, alternative: Alternative) -> tuple[int, int]:
        app_score = 0
        disapp_score = 0
        for ballot, count in self.items():
            if alternative in ballot.approved:
                app_score += count
            if alternative in ballot.disapproved:
                disapp_score += count
        return app_score, disapp_score

    def approval_disapproval_score_dict(self) -> tuple[dict[Alternative, int], dict[Alternative, int]]:
        app_scores = defaultdict(int)
        disapp_scores = defaultdict(int)
        for ballot, count in self.items():
            for alt in ballot.approved:
                app_scores[alt] += count
            for alt in ballot.disapproved:
                disapp_scores[alt] += count
        return app_scores, disapp_scores

    def total(self):
        # Re-implemented as it is not available in Python <3.10
        return sum(self.values())

    def num_ballots(self) -> int:
        return self.total()

    def add_ballot(self, ballot: FrozenTrichotomousBallot):
        """
        Adds a ballot to the profile.
        """
        if isinstance(ballot, TrichotomousBallot):
            raise ValueError("You are trying to add a non-frozen ballot to a multiprofile. This is not possible, "
                             "please freeze the ballot via ballot.freeze() before adding it.")
        self[ballot] += 1

    def multiplicity(self, ballot: FrozenTrichotomousBallot) -> int:
        """
        Returns the multiplicity of a ballot in the profile.

        Parameters
        ----------
            ballot : TrichotomousBallot
                The ballot whose multiplicity is inquired.

        Returns
        -------
            int
                The multiplicity of the ballot.
        """
        return self[ballot]

    def all_sub_profiles(self) -> Iterator[TrichotomousMultiProfile]:
        """
        Returns an iterator that yields all possible sub-profiles.

        Returns
        -------
            Iterator[TrichotomousMultiProfile]
                An iterator that yields all possible sub-profiles.

        """
        items = list(self._ballots_counter.items())
        for counts in product(*(range(count + 1) for _, count in items)):
            sub_profile = TrichotomousMultiProfile({key: count for (key, _), count in zip(items, counts) if count > 0},
                                              alternatives=self.alternatives,
                                              max_size_selection=self.max_size_selection,)
            yield sub_profile

    def __getitem__(self, key):
        return self._ballots_counter[key]

    def __setitem__(self, key, value):
        if value <= 0:
            del self._ballots_counter[key]
        else:
            self._ballots_counter[key] = value

    def __delitem__(self, key):
        del self._ballots_counter[key]

    def __iter__(self):
        return iter(self._ballots_counter)

    def __len__(self):
        return len(self._ballots_counter)

    def __contains__(self, key):
        return key in self._ballots_counter

    def __repr__(self):
        return repr(self._ballots_counter)

    def __str__(self):
        return self._ballots_counter.__str__()

    def __add__(self, other):
        new_profile = TrichotomousMultiProfile(self)
        if isinstance(other, TrichotomousMultiProfile):
            new_profile._ballots_counter = self._ballots_counter + other._ballots_counter
        else:
            new_profile._ballots_counter = self._ballots_counter + other
        return new_profile

    def __iadd__(self, other):
        if isinstance(other, TrichotomousMultiProfile):
            self._ballots_counter += other._ballots_counter
        else:
            self._ballots_counter += other
        return self

    def __sub__(self, other):
        new_profile = TrichotomousMultiProfile(self)
        if isinstance(other, TrichotomousMultiProfile):
            new_profile._ballots_counter = self._ballots_counter - other._ballots_counter
        else:
            new_profile._ballots_counter = self._ballots_counter - other
        return new_profile

    def __isub__(self, other):
        if isinstance(other, TrichotomousMultiProfile):
            self._ballots_counter -= other._ballots_counter
        else:
            self._ballots_counter -= other
        return self

    def __or__(self, other):
        new_profile = TrichotomousMultiProfile(self)
        if isinstance(other, TrichotomousMultiProfile):
            new_profile._ballots_counter = self._ballots_counter | other._ballots_counter
        else:
            new_profile._ballots_counter = self._ballots_counter | other
        return new_profile

    def __ior__(self, other):
        if isinstance(other, TrichotomousMultiProfile):
            self._ballots_counter |= other._ballots_counter
        else:
            self._ballots_counter |= other
        return self

    def __and__(self, other):
        new_profile = TrichotomousMultiProfile(self)
        if isinstance(other, TrichotomousMultiProfile):
            new_profile._ballots_counter = self._ballots_counter & other._ballots_counter
        else:
            new_profile._ballots_counter = self._ballots_counter & other
        return new_profile

    def __iand__(self, other):
        if isinstance(other, TrichotomousMultiProfile):
            self._ballots_counter &= other._ballots_counter
        else:
            self._ballots_counter &= other
        return self

    def elements(self):
        return self._ballots_counter.elements()

    def most_common(self, n=None):
        return self._ballots_counter.most_common(n)

    def subtract(self, other):
        self._ballots_counter.subtract(other)

    def update(self, iterable=None, **kwargs):
        self._ballots_counter.update(iterable, **kwargs)

    def clear(self):
        self._ballots_counter.clear()

    def copy(self):
        return TrichotomousMultiProfile(self)
