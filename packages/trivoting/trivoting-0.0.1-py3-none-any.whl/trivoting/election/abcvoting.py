from abcvoting.fileio import read_abcvoting_yaml_file
from abcvoting.preferences import Profile

from trivoting.election.alternative import Alternative
from trivoting.election.trichotomous_ballot import TrichotomousBallot
from trivoting.election.trichotomous_profile import TrichotomousProfile


def abcvoting_to_trichotomous_profile(abc_profile: Profile) -> TrichotomousProfile:
    """
    Converts a profile from the abcvoting library into a trichotomous profile.

    Parameters
    ----------
        abc_profile : abcvoting.preferences.Profile
            The abcvoting profile to convert.

    Return
    ------
        TrichotomousProfile
            The corresponding trichotomous profile.
    """
    alternatives_map = {i: Alternative(a) for i, a in enumerate(abc_profile.cand_names)}
    profile = TrichotomousProfile(alternatives = alternatives_map.values())
    for abc_ballot in abc_profile:
        ballot = TrichotomousBallot(approved=[alternatives_map[a] for a in abc_ballot.approved])
        profile.add_ballot(ballot)
    return profile

def parse_abcvoting_yaml(file_path) -> TrichotomousProfile:
    """
    Reads a yaml file describing a profile from the abcvoting library and returns a trichotomous profile.

    Parameters
    ----------
        file_path : str
            The path to the abcvoting yaml file.

    Return
    ------
        TrichotomousProfile
            The corresponding trichotomous profile.
    """
    abc_profile, max_size_selection, _, _ = read_abcvoting_yaml_file(file_path)
    profile = abcvoting_to_trichotomous_profile(abc_profile)
    profile.max_size_selection = max_size_selection
    return profile
