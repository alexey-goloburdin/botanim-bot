"""Ranks candidates by the Schulze method.

For more information read http://en.wikipedia.org/wiki/Schulze_method.
"""
import itertools

__author__ = "Michael G. Parker"
__contact__ = "http://omgitsmgp.com/"

from collections import defaultdict


def _add_remaining_ranks(d, candidate, remaining_ranks, weight):
    for remaining_rank in remaining_ranks:
        for other_candidate in remaining_rank:
            d[candidate, other_candidate] += weight


def _add_ranks_to_d(d, ranks, weight):
    for i, rank in enumerate(ranks):
        remaining_ranks = ranks[i + 1 :]
        for candidate in rank:
            _add_remaining_ranks(d, candidate, remaining_ranks, weight)


def _fill_missed_candidates(weighted_ranks, candidates):
    weighted_ranks = list(weighted_ranks)
    for index, rank in enumerate(weighted_ranks):
        flatten_ranks = list(itertools.chain(*rank[0]))
        if len(flatten_ranks) == len(candidates):
            continue
        rest_candidates = [c for c in candidates if c not in flatten_ranks]
        if rest_candidates:
            weighted_ranks[index] = list(rank)
            weighted_ranks[index][0] = list(rank[0])
            weighted_ranks[index][0].append(rest_candidates)
    return weighted_ranks


def _compute_d(weighted_ranks, candidates):
    """Computes the d array in the Schulze method.

    d[V,W] is the number of voters who prefer candidate V over W.
    """
    weighted_ranks = _fill_missed_candidates(weighted_ranks, candidates)
    d = defaultdict(int)
    for ranks, weight in weighted_ranks:
        _add_ranks_to_d(d, ranks, weight)
    return d


def _compute_p(d, candidates):
    """Computes the p array in the Schulze method.

    p[V,W] is the strength of the strongest path from candidate V to W.
    """
    p = {}
    for candidate_1 in candidates:
        for candidate_2 in candidates:
            if candidate_1 != candidate_2:
                strength = d.get((candidate_1, candidate_2), 0)
                if strength > d.get((candidate_2, candidate_1), 0):
                    p[candidate_1, candidate_2] = strength

    for candidate_1 in candidates:
        for candidate_2 in candidates:
            if candidate_1 != candidate_2:
                for candidate_3 in candidates:
                    if (candidate_1 != candidate_3) and (candidate_2 != candidate_3):
                        curr_value = p.get((candidate_2, candidate_3), 0)
                        new_value = min(
                            p.get((candidate_2, candidate_1), 0),
                            p.get((candidate_1, candidate_3), 0),
                        )
                        if new_value > curr_value:
                            p[candidate_2, candidate_3] = new_value

    return p


def _rank_p(candidates, p):
    """Ranks the candidates by p."""
    candidate_wins = defaultdict(list)

    for candidate_1 in candidates:
        num_wins = 0

        # Compute the number of wins this candidate has over all other candidates.
        for candidate_2 in candidates:
            if candidate_1 == candidate_2:
                continue
            candidate1_score = p.get((candidate_1, candidate_2), 0)
            candidate2_score = p.get((candidate_2, candidate_1), 0)
            if candidate1_score > candidate2_score:
                num_wins += 1

        candidate_wins[num_wins].append(candidate_1)

    sorted_wins = sorted(candidate_wins.keys(), reverse=True)
    return [candidate_wins[num_wins] for num_wins in sorted_wins]


def compute_ranks(candidates, weighted_ranks):
    """Returns the candidates ranked by the Schulze method.

    See http://en.wikipedia.org/wiki/Schulze_method for details.

    Parameter candidates is a sequence containing all the candidates.

    Parameter weighted_ranks is a sequence of (ranks, weight) pairs.
    The first element, ranks, is a ranking of the candidates.
    It is an array of arrays so that we
    can express ties. For example, [[a, b], [c], [d, e]] represents a = b > c > d = e.
    The second element, weight, is typically the number of voters that chose
    this ranking.
    """
    d = _compute_d(weighted_ranks, candidates)
    p = _compute_p(d, candidates)
    return _rank_p(candidates, p)
