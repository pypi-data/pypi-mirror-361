# Ranked Pairs Voting

A Python implementation of the Ranked Pairs voting method (also known as Tideman's method), a Condorcet method for conducting fair elections and decision-making processes.

## Overview

The Ranked Pairs voting method is a ranked voting electoral system that can identify a Condorcet winner when one exists. It works by:

1. Conducting pairwise comparisons between all candidates
2. Ranking pairs by their victory margins
3. Building a directed acyclic graph by adding edges in order of margin strength
4. Producing a total ordering of candidates

This implementation handles ties fairly by randomizing their resolution, ensuring no systematic bias.

## Installation

```bash
pip install rankedpairsvoting
```

Or install from source:

```bash
git clone https://github.com/hakai-vulpes/ranked-pairs-voting.git
cd ranked-pairs-voting
pip install -e .
```

## Quick Start

```python
from rankedpairsvoting import ranked_pairs_voting

# Define candidates
candidates = ['Alice', 'Bob', 'Charlie']

# Define votes (lower numbers = higher preference)
votes = [
    [1, 2, 3],  # Voter 1: Alice > Bob > Charlie
    [2, 1, 3],  # Voter 2: Bob > Alice > Charlie
    [3, 1, 2],  # Voter 3: Bob > Charlie > Alice
    [1, 1, 2],  # Voter 4: Alice = Bob > Charlie
]

# Calculate the election result
winners = ranked_pairs_voting(candidates, votes)
print("Election result:", winners)
```

## Vote Format

Votes are represented as lists of integers (or ranks) where:
- **Lower numbers indicate higher preference**
- **Equal numbers indicate tied preferences**
- Each position in the list corresponds to a candidate in the same position in the candidates list

### Examples

```python
candidates = ['Alice', 'Bob', 'Charlie']

# Examples of valid votes:
[1, 2, 3]  # Alice > Bob > Charlie
[2, 1, 1]  # Bob > Alice = Charlie
[1, 1, 2]  # Alice = Bob > Charlie
[2, 2, 1]  # Charlie > Alice = Bob
[1, 1, 1]  # Alice = Bob = Charlie (all tied)

# Example of valid votes due to the algorithm implementation but not correct use
[1, 2, 982193128938129] # Translated to: Alice > Bob > Charlie
[-1, -2, -3] # Translated to: Charlie > Bob > Alice
[1, 1.5, 2] # Translated to: Alice > Bob > Charlie

# Example of invalid votes
['best', 'ok', 'bad']
```

## How It Works

### 1. Pairwise Comparisons

The algorithm first conducts head-to-head comparisons between every pair of candidates:  
(Comparisons are established with valid and correct use votes from above)

```
Alice vs Bob: Tie
Bob vs Charlie: Bob wins 3-1
Alice vs Charlie: Alice wins 2-1
```

### 2. Margin Calculation

Victory margins are calculated for each winning pair:

```
Bob > Alice: margin of 0 and randomly chosen between Alice > Bob or Bob > Alice  
Bob > Charlie: margin of 2  
Alice > Charlie: margin of 1
```

### 3. Graph Construction

Pairs are added to a directed graph in order of decreasing margin strength, ensuring no cycles are created.

### 4. Final Ordering

The graph produces a total ordering of candidates from most preferred to least preferred:  
Bob > Alice > Charlie

## API Reference

### `ranked_pairs_voting(candidates, votes)`

Performs Ranked Pairs voting on the given candidates and votes.

**Parameters:**
- `candidates` (list[str]): List of candidate names in order
- `votes` (list[list[int]]): List of preference rankings for each voter

**Returns:**
- `list[str]`: Ordered list of candidates from winner to last place

**Raises:**
- `ValueError`: If vote format is invalid or candidates list is empty or incomplete

### `PartialOrderGraph`

Internal class used to construct and maintain the directed acyclic graph for candidate ordering.

**Methods:**
- `__init__(nodes: int)`: Initialize graph with specified number of nodes
- `add_edge(big: int, small: int)`: Add a directed edge from big to small
- `add_edges(edges: list[tuple[int, int]])`: Add multiple edges in order of importance
- `get_total_order() -> list[int]`: Return total ordering of nodes

## Examples

### Basic Election

```python
from rankedpairsvoting import ranked_pairs_voting

candidates = ['Candidate A', 'Candidate B', 'Candidate C']
votes = [
    [1, 2, 3],  # A > B > C
    [1, 2, 3],  # A > B > C  
    [2, 1, 3],  # B > A > C
    [3, 2, 1],  # C > B > A
]

result = ranked_pairs_voting(candidates, votes)
print(f"Winner: {result[0]}")
print(f"Full ranking: {result}")
```

### Large Election

```python
candidates = [f"Candidate {i}" for i in range(1, 6)]
votes = []

# Generate 100 random votes
import random
for _ in range(100):
    vote = list(range(1, 6))
    random.shuffle(vote)
    votes.append(vote)

result = ranked_pairs_voting(candidates, votes)
```

## Features

- ✅ **Condorcet Compliant**: Guarantees selection of Condorcet winner when one exists
- ✅ **Tie Handling**: Fair randomized resolution of tied preferences
- ✅ **Efficient**: Polynomial time method, O(n² × v + n² log n) overall (where n = candidates, v = votes)
- ✅ **Flexible**: Supports any number of candidates and voters
- ✅ **Well-Tested**: Comprehensive test suite included
- ✅ **Type Hints**: Full typing support for better IDE integration

## Mathematical Properties

The Ranked Pairs method satisfies several important voting criteria (see [Voting Systems](https://en.wikipedia.org/wiki/Comparison_of_voting_rules#Comparison_of_single-winner_voting_methods)):

- **Condorcet Criterion**: Always elects the Condorcet winner when one exists
- **Reversal Symmetry**: Reversing all preferences reverses the final ordering
- **Local Independence of Irrelevant Alternatives**: The second place is always the winner if the first place is removed, and the second-to-last place becomes the last place if the last place is removed.
- **Independence of Clones**: Adding similar candidates doesn't affect the outcome between dissimilar ones

These criteria make this algorithm one of the soundest for single-winner voting, with the added benefit of it also creating an even more solid ranking of the alternatives. It's only real downside is not satisfying the participation criterion, which could be circumvented by voting in a particular way (selecting at most unique first and second places, but this would lead to a less representative solution).

It is important to take into account that strategically voting requires information. Knowing only the final ranking does not give you enough information, so strategical voting backfires more often than not. However, knowing the ranked pairs margins is enough information to successfully vote strategically, which can affect elections but generally do not decrease voting satisfaction efficiency by a lot (see more [VSE Simulation by Jameson Quinn](https://electionscience.github.io/vse-sim/)).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
git clone https://github.com/hakai-vulpes/ranked-pairs-voting.git
cd ranked-pairs-voting
pip install -e ".[dev]"
```

### Running Tests

```bash
python -m pytest tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## References

- [Tideman, T. Nicolaus (1987). "Independence of clones as a criterion for voting rules". Social Choice and Welfare.](https://link.springer.com/article/10.1007/BF00433944)
- [Wikipedia: Ranked Pairs](https://en.wikipedia.org/wiki/Ranked_pairs)
- [Condorcet Internet Voting Service](https://civs.cs.cornell.edu/)

## Disclaimer
Documentation was written with AI and carefully revised by me, if there are any issues please notify me.

## Changelog

### v0.0.1 (Initial Release)
- Basic Ranked Pairs implementation
- Support for tied preferences
- Graph-based candidate ordering
- Comprehensive documentation and examples