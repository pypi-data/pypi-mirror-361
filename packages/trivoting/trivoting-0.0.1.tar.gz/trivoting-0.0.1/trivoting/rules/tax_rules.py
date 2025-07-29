from __future__ import annotations

from collections.abc import Collection, Callable

import pabutools.election as pb_election
import pabutools.rules as pb_rules

from trivoting.election.alternative import Alternative
from trivoting.election.trichotomous_profile import AbstractTrichotomousProfile
from trivoting.fractions import frac
from trivoting.rules.selection import Selection
from trivoting.tiebreaking import TieBreakingRule


def tax_pb_instance(
        profile: AbstractTrichotomousProfile,
        max_size_selection: int,
        initial_selection: Selection | None = None,
):
    """
    Returns a Participatory Budgeting instance and profile based on the given trichotomous profile.
    """
    app_scores, disapp_scores = profile.approval_disapproval_score_dict()

    if initial_selection is None:
        initial_selection = Selection()

    alt_to_project = dict()
    project_to_alt = dict()
    running_alternatives = set()
    pb_instance = pb_election.Instance(budget_limit=max_size_selection)
    for alt, app_score in app_scores.items():
        support = app_score - disapp_scores[alt]
        if support > 0 and alt not in initial_selection:
            project = pb_election.Project(alt.name, cost=frac(app_score, support))
            pb_instance.add(project)
            running_alternatives.add(alt)
            alt_to_project[alt] = project
            project_to_alt[project] = alt

    pb_profile = pb_election.ApprovalMultiProfile(instance=pb_instance)
    for ballot in profile:
        pb_profile.append(
            pb_election.FrozenApprovalBallot(alt_to_project[alt] for alt in ballot.approved if alt in running_alternatives)
        )
    return pb_instance, pb_profile, project_to_alt

def tax_pb_rule_scheme(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    pb_rule: Callable,
    initial_selection: Selection | None = None,
    tie_breaking: TieBreakingRule | None = None,
    resoluteness: bool = True,
    pb_rule_kwargs: dict = None,
) -> Selection | list[Selection]:
    """
    Runs the tax rule scheme. Defined the appropriate Participatory Budgeting (PB) instance and apply the required PB
    rule to that instance. Makes use of the pabutools package for the PB side.

    Parameters
    ----------
        profile : AbstractTrichotomousProfile
            The profile.
        max_size_selection : int
            The maximum number of alternatives that can be selected.
        pb_rule : Callable
            The PB rule to apply.
        initial_selection: Selection, optional
            An initial selection, fixed some alternatives has being either selected of not-selected. If the
            selection has implicit_reject set to `True`, then no alternative is forced not-selected.
        tie_breaking : TieBreakingRule, optional
            The tie-breaking rule used.
            Defaults to the lexicographic tie-breaking.
        resoluteness : bool, optional
            Set to `False` to obtain an irresolute outcome, where all tied budget allocations are returned.
            Defaults to True.
        pb_rule_kwargs: dict, optional
            Additional keyword arguments to pass to the PB rule.

    Returns
    -------
        Selection | list[Selection]
            The selection if resolute (:code:`resoluteness == True`), or a list of selections
            if irresolute (:code:`resoluteness == False`).
    """
    if pb_rule_kwargs is None:
        pb_rule_kwargs = dict()

    if initial_selection is None:
        initial_selection = Selection(implicit_reject=True)

    if profile.num_ballots() == 0:
        return initial_selection if resoluteness else [initial_selection]

    pb_instance, pb_profile, project_to_alt = tax_pb_instance(profile, max_size_selection, initial_selection)

    budget_allocation = pb_rule(
        pb_instance,
        pb_profile,
        tie_breaking=tie_breaking,
        resoluteness=resoluteness,
        **pb_rule_kwargs
    )

    if resoluteness:
        initial_selection.extend_selected(project_to_alt[p] for p in budget_allocation)
        if not initial_selection.implicit_reject:
            initial_selection.extend_rejected(project_to_alt[p] for p in pb_instance if p not in budget_allocation)
        return initial_selection
    else:
        all_selections = []
        for alloc in budget_allocation:
            selection = initial_selection.copy()
            selection.extend_selected(project_to_alt[p] for p in alloc)
            if not selection.implicit_reject:
                selection.extend_rejected(project_to_alt[p] for p in pb_instance if p not in alloc)
            all_selections.append(selection)
        return all_selections

def tax_method_of_equal_shares(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    initial_selection: Selection | None = None,
    tie_breaking: TieBreakingRule | None = None,
    resoluteness: bool = True,
) -> Selection | list[Selection]:
    """
    Tax method of equal shares.

    Parameters
    ----------
        profile : AbstractTrichotomousProfile
            The profile.
        max_size_selection : int
            The maximum number of alternatives that can be selected.
        initial_selection: Selection, optional
            An initial selection, fixed some alternatives has being either selected of not-selected. If the
            selection has implicit_reject set to `True`, then no alternative is forced not-selected.
        tie_breaking : TieBreakingRule, optional
            The tie-breaking rule used.
            Defaults to the lexicographic tie-breaking.
        resoluteness : bool, optional
            Set to `False` to obtain an irresolute outcome, where all tied budget allocations are returned.
            Defaults to True.

    Returns
    -------
        Selection | list[Selection]
            The selection if resolute (:code:`resoluteness == True`), or a list of selections
            if irresolute (:code:`resoluteness == False`).
    """
    return tax_pb_rule_scheme(
        profile,
        max_size_selection,
        pb_rules.method_of_equal_shares,
        initial_selection=initial_selection,
        tie_breaking=tie_breaking,
        resoluteness=resoluteness,
        pb_rule_kwargs={"sat_class": pb_election.Cardinality_Sat}
    )

def tax_sequential_phragmen(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    initial_selection: Selection | None = None,
    tie_breaking: TieBreakingRule | None = None,
    resoluteness: bool = True,
) -> Selection | list[Selection]:
    """
    Tax sequential Phragmén.

    Parameters
    ----------
        profile : AbstractTrichotomousProfile
            The profile.
        max_size_selection : int
            The maximum number of alternatives that can be selected.
        initial_selection: Selection, optional
            An initial selection, fixed some alternatives has being either selected of not-selected. If the
            selection has implicit_reject set to `True`, then no alternative is forced not-selected.
        tie_breaking : TieBreakingRule, optional
            The tie-breaking rule used.
            Defaults to the lexicographic tie-breaking.
        resoluteness : bool, optional
            Set to `False` to obtain an irresolute outcome, where all tied budget allocations are returned.
            Defaults to True.

    Returns
    -------
        Selection | list[Selection]
            The selection if resolute (:code:`resoluteness == True`), or a list of selections
            if irresolute (:code:`resoluteness == False`).
    """

    return tax_pb_rule_scheme(
        profile,
        max_size_selection,
        pb_rules.sequential_phragmen,
        initial_selection=initial_selection,
        tie_breaking=tie_breaking,
        resoluteness=resoluteness,
        pb_rule_kwargs={"global_max_load": frac(max_size_selection, profile.num_ballots()) if profile.num_ballots() else None}
    )
