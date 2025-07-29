from collections.abc import Iterable, Iterator
from itertools import combinations


def generate_subsets(it: Iterable, *, min_size: int = None, max_size: int = None) -> Iterator:
    elements = tuple(it)
    if min_size is None:
        min_size = 0
    if max_size is None:
        max_size = len(elements)
    for r in range(min_size, max_size + 1):
        for c in combinations(elements, r):
            yield c


def generate_two_list_partitions(iterable: Iterable, first_list_max_size=None) -> Iterator[tuple[list, list]]:
    elements = list(iterable)
    n = len(elements)

    # print("START")
    # Generate all non-empty subsets (powerset)
    for r in range(0, n + 1):
        for subset in combinations(elements, r):
            # print("\tsub=", subset)
            subset = list(subset)
            for s in range(0, len(subset) + 1):
                for subset_subset in combinations(subset, s):
                    # print("\t\tsubsub=", subset_subset)
                    if first_list_max_size is not None and len(subset_subset) > first_list_max_size:
                        continue
                    part1 = []
                    part2 = []
                    for e in subset:
                        if e in subset_subset:
                            part1.append(e)
                        else:
                            part2.append(e)
                    # print("\t\t->", part1, part2)
                    yield part1, part2
                    # Break to avoid having [], [] twice
                    if len(part1) == 0 == len(part2):
                        break
