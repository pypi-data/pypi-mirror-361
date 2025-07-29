class PartialOrderGraph:
    """Graph that interprets partial order relations between nodes."""

    def __init__(self, nodes: int):
        if nodes < 1:
            raise ValueError("Number of nodes must be at least 1.")

        self.n = nodes
        self.direct_lower: list[set[int]] = [set() for _ in range(nodes)]
        self.lower: list[set[int]] = [set() for _ in range(nodes)]
        self.direct_upper: list[set[int]] = [set() for _ in range(nodes)]
        self.upper: list[set[int]] = [set() for _ in range(nodes)]

    def __checks(self, big: int, small: int) -> bool:
        if not (0 <= big < self.n and 0 <= small < self.n):
            raise ValueError("Both nodes must be in the graph.")

        if big == small:
            raise ValueError("Cannot add an edge from a node to itself.")

        if small in self.lower[big]:
            return False  # If big > small is already true, do nothing

        if big in self.lower[small]:
            return False  # Avoid adding a cycle

        return True

    def add_edges(self, edges: list[tuple[int, int]]):
        """
        Add multiple edges to the graph. They must be ordered from most to least
        important edge.

        Args:
            edges (list[tuple[int, int]]): List of edges to add, where each edge is a
                tuple (big, small) and they are ordered from most to least important
                edge.
        """

        for big, small in edges:
            self.add_edge(big, small)

    def _update_upwards(self, node: int, nodes: set[int]):
        # Update the direct links
        self.direct_lower[node] = self.direct_lower[node] - nodes

        # We can assume that for every upper node, it includes all of the lower nodes
        nodes = nodes - self.lower[node]
        if not nodes:
            return

        # Update the lower set
        self.lower[node].update(nodes)

        # Avoid adding recursion to the stack if unnecessary
        while len(neighbors := self.direct_upper[node]) == 1:
            node = next(iter(neighbors))

            # Update the direct links
            self.direct_lower[node] = self.direct_lower[node] - nodes

            nodes = nodes - self.lower[node]
            if not nodes:
                return

            # Update the lower set
            self.lower[node].update(nodes)

        # Recursively update all neighbors
        for neighbor in neighbors:
            self._update_upwards(neighbor, nodes)

    def _update_downwards(self, node: int, nodes: set[int]):
        # Update the direct links
        self.direct_upper[node] = self.direct_upper[node] - nodes

        # We can assume that for every lower node, it includes all of the upper nodes
        nodes = nodes - self.upper[node]
        if not nodes:
            return

        # Update the upper set
        self.upper[node].update(nodes)

        # Avoid adding recursion to the stack if unnecessary
        while len(neighbors := self.direct_lower[node]) == 1:
            node = next(iter(neighbors))

            # Update the direct links
            self.direct_upper[node] = self.direct_upper[node] - nodes

            nodes = nodes - self.upper[node]
            if not nodes:
                return

            # Update the upper set
            self.upper[node].update(nodes)

        # Recursively update all neighbors
        for neighbor in neighbors:
            self._update_downwards(neighbor, nodes)

    def add_edge(self, big: int, small: int):
        """
        Add an edge to the graph.

        Args:
            big (int): The node that is greater in the order.
            small (int): The node that is smaller in the order.
        """

        if not (temp := self.__checks(big, small)):
            return temp

        # Update lower and upper sets
        bottom_nodes = self.lower[small] | {small}
        self._update_upwards(big, bottom_nodes)
        top_nodes = self.upper[big] | {big}
        self._update_downwards(small, top_nodes)

        # Update direct links
        self.direct_lower[big].add(small)
        self.direct_upper[small].add(big)

    def get_total_order(self) -> list[int]:
        """
        Retrieve the total order of the graph.

        Returns:
            order (list[int]): A list of nodes in total order.

        Raises:
            ValueError: If the graph is not a total order.
        """
        # Find the head of the graph
        n = 0
        while parents := self.direct_upper[n]:
            if len(parents) > 2:
                raise ValueError("Graph is not a total order.")
            n = parents.pop()

        # Retrieve the total order
        order = [n]
        while children := self.direct_lower[n]:
            if len(children) > 2:
                raise ValueError("Graph is not a total order.")
            n = children.pop()
            order.append(n)

        if len(order) != self.n:
            raise ValueError("Graph is not a total order.")

        return order


if __name__ == "__main__":
    candidates = [2, 1, 3, 4, 0]
    vote = [[4, 1, 5, 3, 2]]
    edges = [
        (4, 2),
        (0, 2),
        (1, 2),
        (3, 2),
        (1, 4),
        (1, 3),
        (4, 0),
        (3, 0),
        (1, 0),
        (4, 3),
    ]
    graph = PartialOrderGraph(5)
    graph.add_edges(edges)
    result = [candidates[node] for node in graph.get_total_order()]
    print(
        result,
        [
            (candidates[candidate], position)
            for candidate, position in enumerate(vote[0])
        ],
        [result[position - 1] for candidate, position in enumerate(vote[0])],
    )
    assert all(
        result[position - 1] == candidates[candidate]
        for candidate, position in enumerate(vote[0])
    )
