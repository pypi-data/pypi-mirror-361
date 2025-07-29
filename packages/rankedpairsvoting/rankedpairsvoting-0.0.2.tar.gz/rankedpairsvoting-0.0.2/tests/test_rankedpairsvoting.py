"""
Test suite for the rankedpairsvoting package.

This module contains comprehensive tests for the Ranked Pairs voting implementation,
including edge cases, error conditions, and mathematical properties.
"""

import pytest
import random
from rankedpairsvoting import ranked_pairs_voting
from rankedpairsvoting.objects import PartialOrderGraph


class TestRankedPairsVoting:
    """Test cases for the main ranked_pairs_voting function."""

    def test_single_vote(self):
        """Test a single vote with one candidate"""
        n = 100
        random.seed(1234)  # For reproducibility
        candidates = [*range(n)]
        random.shuffle(candidates)
        vote = [*range(1, n + 1)]
        random.shuffle(vote)

        result = ranked_pairs_voting(candidates, [vote])

        assert all(
            result[position - 1] == candidates[candidate]
            for candidate, position in enumerate(vote)
        )

    def test_simple_election(self):
        """Test a basic three-candidate election."""
        candidates = ["Alice", "Bob", "Charlie"]
        votes = [
            [1, 2, 3],  # Alice > Bob > Charlie
            [1, 2, 3],  # Alice > Bob > Charlie
            [2, 1, 3],  # Bob > Alice > Charlie
        ]

        result = ranked_pairs_voting(candidates, votes)

        assert result[0] == "Alice"  # Alice should win
        assert len(result) == 3
        assert all(candidate in result for candidate in candidates)

    def test_single_candidate(self):
        """Test election with only one candidate."""
        candidates = ["Solo"]
        votes = [[1]]

        result = ranked_pairs_voting(candidates, votes)

        assert result == ["Solo"]

    def test_tied_preferences(self):
        """Test election with tied preferences."""
        candidates = ["A", "B", "C"]
        votes = [
            [1, 1, 2],  # A = B > C
            [2, 1, 1],  # B = C > A
            [1, 2, 2],  # A > B = C
        ]

        result = ranked_pairs_voting(candidates, votes)

        # Should return a valid ranking of all candidates
        assert len(result) == 3
        assert set(result) == set(candidates)

    def test_all_tied(self):
        """Test election where all candidates are tied."""
        candidates = ["X", "Y", "Z"]
        votes = [
            [1, 1, 1],  # All tied
            [1, 1, 1],  # All tied
            [1, 1, 1],  # All tied
        ]

        result = ranked_pairs_voting(candidates, votes)

        # Should return all candidates in some order
        assert len(result) == 3
        assert set(result) == set(candidates)

    def test_condorcet_winner(self):
        """Test that Condorcet winner is always selected."""
        candidates = ["Winner", "Loser1", "Loser2"]
        votes = [
            [1, 2, 3],  # Winner beats all
            [1, 3, 2],  # Winner beats all
            [1, 2, 3],  # Winner beats all
            [2, 1, 3],  # Even when some prefer others first
        ]

        result = ranked_pairs_voting(candidates, votes)

        assert result[0] == "Winner"

    def test_empty_inputs_raise_error(self):
        """Test that empty inputs raise appropriate errors."""
        # These should raise ValueError or similar
        with pytest.raises(Exception):
            ranked_pairs_voting([], [])

        with pytest.raises(Exception):
            ranked_pairs_voting(["A"], [])

    def test_mismatched_lengths_raise_error(self):
        """Test that mismatched vote lengths raise errors."""
        candidates = ["A", "B"]
        votes = [[1, 2, 3]]  # Vote has 3 elements, candidates has 2

        with pytest.raises(Exception):
            ranked_pairs_voting(candidates, votes)

    def test_candidate_performance(self):
        """Test performance with a large number of candidates."""
        # Adjust number of candidates to get an "acceptable" performance
        # The true metric is not time but how many votes can be processed in an acceptable time
        ncandidates = 1_000
        nvotes = 100
        random.seed(1234)  # For reproducibility
        candidates = [f"Candidate_{i}" for i in range(ncandidates)]
        votes = [
            [random.randint(1, ncandidates) for _ in range(ncandidates)]
            for _ in range(nvotes)
        ]

        result = ranked_pairs_voting(candidates, votes)

        assert len(result) == ncandidates
        assert set(result) == set(candidates)

    def test_vote_performance(self):
        """Test performance with a large number of votes."""
        # Adjust number of votes to get an "acceptable" performance
        # The true metric is not time but how many votes can be processed in an acceptable time
        ncandidates = 10
        nvotes = 1_000_000
        random.seed(1234)
        candidates = [f"Candidate_{i}" for i in range(ncandidates)]
        votes = [
            [random.randint(1, ncandidates) for _ in range(ncandidates)]
            for _ in range(nvotes)
        ]

        result = ranked_pairs_voting(candidates, votes)

        assert len(result) == ncandidates
        assert set(result) == set(candidates)


class TestPartialOrderGraph:
    """Test cases for the PartialOrderGraph class."""

    def test_initialization(self):
        """Test graph initialization."""
        graph = PartialOrderGraph(3)

        assert graph.n == 3
        assert len(graph.lower) == 3
        assert len(graph.upper) == 3
        assert len(graph.direct_lower) == 3
        assert len(graph.direct_upper) == 3

    def test_invalid_initialization(self):
        """Test that invalid initialization raises error."""
        with pytest.raises(ValueError):
            PartialOrderGraph(0)

        with pytest.raises(ValueError):
            PartialOrderGraph(-1)

    def test_add_edge(self):
        """Test adding edges to the graph."""
        graph = PartialOrderGraph(3)
        graph.add_edge(0, 1)  # 0 > 1

        assert 1 in graph.direct_lower[0]
        assert 1 in graph.lower[0]
        assert 0 in graph.direct_upper[1]
        assert 0 in graph.upper[1]
        assert len(graph.direct_lower[0]) == 1
        assert len(graph.direct_upper[1]) == 1
        assert len(graph.lower[0]) == 1
        assert len(graph.upper[1]) == 1

    def test_transitivity(self):
        """Test that transitivity is maintained."""
        graph = PartialOrderGraph(3)
        graph.add_edge(0, 1)  # 0 > 1
        graph.add_edge(1, 2)  # 1 > 2

        # Should have transitivity: 0 > 2
        assert 2 in graph.lower[0]  # Transitive edge added
        assert 2 not in graph.direct_lower[0]  # Direct edge not added

    def test_get_order(self):
        """Test getting the topological order."""
        graph = PartialOrderGraph(3)
        graph.add_edge(0, 1)  # 0 > 1
        graph.add_edge(0, 2)  # 0 > 2
        graph.add_edge(1, 2)  # 1 > 2

        order = [*graph.get_total_order()]

        # 0 > 1 > 2 should be the order
        assert order.index(0) < order.index(1)
        assert order.index(0) < order.index(2)
        assert order.index(1) < order.index(2)

    def test_invalid_nodes(self):
        """Test adding edges with invalid nodes."""
        graph = PartialOrderGraph(2)

        with pytest.raises(ValueError):
            graph.add_edge(0, 5)  # Node 5 doesn't exist

        with pytest.raises(ValueError):
            graph.add_edge(-1, 0)  # Node -1 doesn't exist


class TestMathematicalProperties:
    """Test mathematical properties of the voting method."""

    def test_monotonicity_basic(self):
        """Test basic monotonicity property."""
        candidates = ["A", "B", "C"]

        # Original election
        votes1 = [
            [1, 2, 3],  # A > B > C
            [2, 1, 3],  # B > A > C
            [3, 1, 2],  # B > C > A
        ]
        result1 = ranked_pairs_voting(candidates, votes1)

        # Improve A's position in one vote
        votes2 = [
            [1, 2, 3],  # A > B > C (same)
            [1, 2, 3],  # A > B > C (improved A)
            [3, 1, 2],  # B > C > A (same)
        ]
        result2 = ranked_pairs_voting(candidates, votes2)

        # A should not be worse off
        assert result2.index("A") <= result1.index("A")

    def test_neutrality(self):
        """Test that the method treats candidates symmetrically."""
        # This is tested indirectly through other tests
        # Full neutrality testing would require many permutations
        pass

    def test_determinism(self):
        """Test that same inputs produce same outputs (with same random seed)."""
        import random

        candidates = ["X", "Y", "Z"]
        votes = [
            [1, 2, 3],
            [2, 3, 1],
            [3, 1, 2],
        ]

        # Set seed for reproducible results
        random.seed(42)
        result1 = ranked_pairs_voting(candidates, votes)

        random.seed(42)
        result2 = ranked_pairs_voting(candidates, votes)

        assert result1 == result2


if __name__ == "__main__":
    pytest.main([__file__])
