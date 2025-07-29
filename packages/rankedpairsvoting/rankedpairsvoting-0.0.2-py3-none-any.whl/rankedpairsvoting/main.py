import random
from itertools import combinations, permutations
from .objects import PartialOrderGraph


def perform_round_robin(votes: list[list[int]]) -> dict[tuple[int, int], int]:
    """
    Conducts a round-robin tournament among candidates based on the votes.

    Args:
        votes (list[list[int]]): A list of votes, where each vote is a list of
        candidate rankings.

    Returns:
        dict[tuple[int, int], int]: A dictionary containing the pairwise
        preferences between candidates.
    """

    round_robin = {(i, j): 0 for i, j in permutations(range(len(votes[0])), 2)}
    for vote in votes:
        for i, j in combinations(range(len(vote)), 2):
            if vote[i] < vote[j]:
                round_robin[(i, j)] += 1
            elif vote[i] > vote[j]:
                round_robin[(j, i)] += 1

    return round_robin


def calculate_pairwise_margins(
    round_robin: dict[tuple[int, int], int],
    N: int,
) -> tuple[dict[tuple[int, int], int], list[tuple[int, int]]]:
    """
    Calculates the pairwise margins between candidates based on the votes and sorts
    them. Also determines ties.

    Args:
        votes (list[list[int]]): A list of votes, where each vote is a list of
            candidate rankings.
        N (int): The number of candidates.

    Returns:
        tuple[dict[tuple[int, int], int], list[tuple[int, int]]]: A tuple containing
            the pairwise margins between candidates, the dictionary, and a list of
            pairs of candidates that are tied.
    """

    ties = []
    # Calculate the pairwise margins only keeping winning pairs
    pairwise_margins = dict()
    for i, j in combinations(range(N), 2):
        if round_robin[(i, j)] > round_robin[(j, i)]:
            pairwise_margins[(i, j)] = round_robin[(i, j)] - round_robin[(j, i)]
        elif round_robin[(i, j)] < round_robin[(j, i)]:
            pairwise_margins[(j, i)] = round_robin[(j, i)] - round_robin[(i, j)]
        else:
            # Ties are very coincidental may cause non-orderability if not
            # taken into account. Therefore, we determine them at random which
            # is fair for candidates and will have the lowest priority of pairs
            # in terms of ordering.
            if random.getrandbits(1) == 1:
                ties.append((i, j))
            else:
                ties.append((j, i))

    # Shuffle for fairness and sort by margin
    # Otherwise pairs may favor candidates placed first in the list
    random.shuffle(ties)
    return pairwise_margins, ties


def ranked_pairs_voting(candidates: list[str], votes: list[list[int]]) -> list[str]:
    """
    Effectuates the Ranked Pairs voting method.

    Args:
        candidates (list[str]): A list of candidate names in order.
        votes (list[list[int]]): A list of votes, ranking each candidate in the
            voter's preference order. There can be multiple candidates in the
            same position.

    Returns:
        winners (list[str]): The list of winning candidates in order.

    """
    if len(candidates) < 1:
        raise ValueError("There must be at least one candidate.")

    if len(votes) < 1:
        raise ValueError("There must be at least one vote.")

    if any(len(vote) != len(candidates) for vote in votes):
        raise ValueError("All votes must have the same number of candidates.")

    # Effectuate round-robin to determine pairwise preferences
    round_robin_result = perform_round_robin(votes)
    pairwise_margins, ties = calculate_pairwise_margins(
        round_robin_result, len(candidates)
    )

    pairwise_margins_list = [*pairwise_margins.items()]
    random.shuffle(pairwise_margins_list)
    sorted_pairs = sorted(pairwise_margins_list, key=lambda x: x[1], reverse=True)

    # Construct the graph with total ordering of candidates
    graph = PartialOrderGraph(len(candidates))
    graph.add_edges([(big, small) for (big, small), _ in sorted_pairs])
    graph.add_edges(ties)

    # Get the final order of candidates
    return [candidates[i] for i in graph.get_total_order()]


if __name__ == "__main__":
    # Example usage
    candidates = ["Alice", "Bob", "Charlie"]
    votes = [
        [1, 2, 3],  # Voter 1 prefers Alice > Bob > Charlie
        [2, 1, 3],  # Voter 2 prefers Bob > Alice > Charlie
        [3, 1, 2],  # Voter 3 prefers Bob > Charlie > Alice
        [1, 1, 2],  # Voter 4 prefers Alice = Bob > Charlie
        [1, 1, 1],  # Voter 5 prefers Alice = Bob = Charlie
        [2, 2, 1],  # Voter 6 prefers Charlie > Bob = Alice
        [2, 2, 1],  # Voter 7 prefers Charlie > Bob = Alice
    ]

    winners = ranked_pairs_voting(candidates, votes)
    print("Winners:", winners)
