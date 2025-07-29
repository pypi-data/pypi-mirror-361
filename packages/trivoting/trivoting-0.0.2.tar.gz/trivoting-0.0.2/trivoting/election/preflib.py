from __future__ import annotations

from preflibtools.instances import CategoricalInstance, get_parsed_instance

from trivoting.election.alternative import Alternative
from trivoting.election.trichotomous_ballot import TrichotomousBallot
from trivoting.election.trichotomous_profile import TrichotomousProfile


def cat_preferences_to_trichotomous_ballot(pref: tuple[tuple[int]], alt_map: dict[int, Alternative]) -> TrichotomousBallot:
    """Converts a categorical preference as defined in the PrefLib standard into a trichotomous ballot.
    The first category is mapped to the "approved alternatives". The second category is mapped to the "neutral
    alternatives". The last category is mapped to the "disapproved alternatives".

    Parameters
    ----------
        pref: tuple[tuple[int]]
            The preferences as represented in the preflibtools' CategoricalInstance.
        alt_map: dict[int, Alternative]
            A dictionary mapping alternative names in PrefLib (int) to Alternative objects.

    Returns
    -------
        TrichotomousBallot
            The trichotomous ballot.
    """
    if len(pref) == 0 or len(pref) > 3:
        raise ValueError("Only categorical preferences between 1 and 3 categories can be converted to"
                         f"a trichotomous ballot. Pref {pref} has {len(pref)} categories.")
    ballot = TrichotomousBallot(approved=[alt_map[j] for j in pref[0]])
    if len(pref) < 2:
        return ballot
    ballot.disapproved = [alt_map[j] for j in pref[-1]]
    return ballot


def cat_instance_to_trichotomous_profile(cat_instance: CategoricalInstance) -> TrichotomousProfile:
    """Converts a PrefLib Categorical instance into a Trichotomous Profile."""
    if cat_instance.num_categories == 0 or cat_instance.num_categories > 3:
        raise ValueError("Only categorical preferences between 1 and 3 categories can be converted to"
                         f"a trichotomous profile. Categorical instance {cat_instance} has "
                         f"{cat_instance.num_categories} categories.")

    alt_map = {j: Alternative(j) for j in cat_instance.alternatives_name}
    profile = TrichotomousProfile(alternatives=alt_map.values())

    for p, m in cat_instance.multiplicity.items():
        for _ in range(m):
            profile.append(cat_preferences_to_trichotomous_ballot(p, alt_map))
    return profile

def parse_preflib(file_path: str) -> TrichotomousProfile:
    """
    Parses a PrefLib file and returns the corresponding trichotomous profile.

    Parameters
    ----------
        file_path : str
            Path to the PrefLib file to be parsed.

    Returns
    -------
        TrichotomousProfile
            The profile corresponding to the file.
    """

    instance = get_parsed_instance(file_path, autocorrect=True)
    if isinstance(instance, CategoricalInstance):
        return cat_instance_to_trichotomous_profile(instance)
    raise ValueError(f"PrefLib instances of type {type(instance)} cannot be converted to trichotomous profiles.")
