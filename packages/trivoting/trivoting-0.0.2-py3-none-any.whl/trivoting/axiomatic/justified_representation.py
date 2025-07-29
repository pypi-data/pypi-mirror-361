from collections.abc import Iterable, Iterator

from trivoting.election.alternative import Alternative
from trivoting.election.trichotomous_ballot import AbstractTrichotomousBallot
from trivoting.election.trichotomous_profile import AbstractTrichotomousProfile
from trivoting.fractions import frac
from trivoting.rules.selection import Selection
from trivoting.utils import generate_subsets


def is_cohesive_for_l(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    l: int,
    group: AbstractTrichotomousProfile
) -> bool:
    """
    Tests whether the given set of voters is cohesive.
    """
    if l > max_size_selection:
        return False
    if l == 0:
        return True
    if group.num_ballots() == 0:
        return False

    commonly_approved_alts = set.intersection(*(set(ballot.approved) for ballot in group))
    # Does not matter if we can find subsets with more than l
    commonly_approved_alts_subsets = list(generate_subsets(commonly_approved_alts, min_size=l, max_size=l))

    # Shortcut if there are no commonly approved alternatives of the suitable size
    if len(commonly_approved_alts_subsets) == 0:
        return l == 0

    group_size = sum(group.multiplicity(b) for b in group)
    relative_group_size = frac(group_size, profile.num_ballots())
    for selection in profile.all_feasible_selections(max_size_selection):
        if relative_group_size <= frac(l, selection.total_len() + l):
            return False
        exists_set_x = False
        for extra_alts in commonly_approved_alts_subsets:
            if any(a in selection.rejected for a in extra_alts):
                continue
            if len(set(extra_alts).union(selection.selected)) <= max_size_selection:
                exists_set_x = True
        if not exists_set_x:
            return False
    return True


def all_cohesive_groups(profile: AbstractTrichotomousProfile, max_size_selection: int, min_l = 1, max_l = None) -> Iterator[tuple[AbstractTrichotomousProfile, int]]:
    if max_l is None:
        max_l = len(profile.alternatives)
    for group in profile.all_sub_profiles():
        for l in range(min_l, max_l + 1):
            if is_cohesive_for_l(profile, max_size_selection, l, group):
                yield group, l

def is_base_ejr(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    selection: Selection
):
    """
    Tests whether the given selection satisfies Base Extended Justified Representation (Base EJR) for the given
    profile.
    """

    for group, l in all_cohesive_groups(profile, max_size_selection):
        group_satisfied = False
        for ballot in group:
            satisfaction = sum(1 for a in ballot.approved if selection.is_selected(a))
            satisfaction += sum(1 for a in ballot.disapproved if not selection.is_selected(a))
            if satisfaction >= l:
                group_satisfied = True
                break
        if not group_satisfied:
            return False
    return True

def is_base_pjr(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    selection: Selection
):
    """
    Tests whether the given selection satisfies Base Proportional Justified Representation (Base PJR) for the given
    profile.
    """

    for group, l in all_cohesive_groups(profile, max_size_selection):
        coincident_alternatives = set()
        for ballot in group:
            coincident_alternatives.update(a for a in ballot.approved if selection.is_selected(a))
            coincident_alternatives.update(a for a in ballot.disapproved if not selection.is_selected())
        if len(coincident_alternatives) < l:
            return False
    return True
