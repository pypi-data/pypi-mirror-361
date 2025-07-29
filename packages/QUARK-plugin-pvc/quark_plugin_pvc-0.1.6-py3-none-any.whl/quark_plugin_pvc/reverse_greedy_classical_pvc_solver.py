from dataclasses import dataclass
from typing import override

from quark.core import Core, Data, Result
from quark.interface_types import Graph, Other


@dataclass
class ReverseGreedyClassicalPvcSolver(Core):
    @override
    def preprocess(self, data: Graph) -> Result:
        graph = data.as_nx_graph()
        # Need to deep copy since we are modifying the graph in this function.
        # Else the next repetition would work with a different graph
        mapped_problem = graph.copy()

        # We always start at the base node
        current_node = ((0, 0), 1, 1)
        idx = 1

        tour = {current_node + (0,): 1}

        # Tour needs to cover all nodes, if there are 2 nodes left we can finish since these 2 nodes
        # belong to the same seam
        while len(mapped_problem.nodes) > 2:
            # Get the minimum neighbor edge from the current node
            # TODO This only works if the artificial high edge weights are exactly 100000
            next_node = max(
                (
                    x
                    for x in mapped_problem.edges(current_node[0], data=True)
                    if x[2]["c_start"] == current_node[1]
                    and x[2]["t_start"] == current_node[2]
                    and x[2]["weight"] != 100000
                ),
                key=lambda x: x[2]["weight"],
            )
            next_node = (next_node[1], next_node[2]["c_end"], next_node[2]["t_end"])

            # Make the step - add distance to cost, add the best node to tour,
            tour[next_node + (idx,)] = 1

            # Remove all node of that seam
            to_remove = [x for x in mapped_problem.nodes if x[0] == current_node[0][0]]
            for node in to_remove:
                mapped_problem.remove_node(node)

            current_node = next_node
            idx += 1

        # Tour needs to look like {((0, 0), 1, 1, 0): 1,((3, 1), 1, 0, 1): 1,((2, 1), 1, 1, 2): 1,((4, 4), 1, 1, 3): 1}
        # ((0, 0), 1, 1, 0): 1 = ((seam, node), config, tool, timestep): yes we visit this
        self._tour = tour

        return Data(None)

    @override
    def postprocess(self, data: None) -> Result:
        filtered_tour = [x[0] for x in self._tour.items() if x[1] == 1]
        filtered_tour.sort(key=lambda x: x[-1])
        filtered_tour = [x[:-1] for x in filtered_tour]

        return Data(Other(filtered_tour))
