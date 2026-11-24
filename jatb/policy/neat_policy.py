import math
from collections import deque
from collections.abc import Sequence
from jatb.neat import Genome
from .Ipolicy import IPolicy

SIGMOID_STEEPNESS = 4.9

class NeatPolicy(IPolicy):
    def __init__(self,
                 genome: Genome,
                 input_ids: Sequence[int],
                 bias_id: int,
                 output_ids: Sequence[int]) -> None:
        self.input_ids = input_ids
        self.bias_id = bias_id
        self.output_ids = output_ids
        self.output_size = len(output_ids)

        G = self.__create_graph(genome)
        self.G_inverted = self.__create_inverted_graph(genome)

        source_ids = {*input_ids, bias_id}
        evaluation_order = self.__sort_topologically(G, self.G_inverted)
        self.evaluation_order = [node_id for node_id in evaluation_order if node_id not in source_ids]
        
    @staticmethod
    def __create_graph(genome: Genome) -> dict[int, list[int]]:
        """ from -> [to] if from -> to is enabled"""
        G: dict[int, list[int]] = {node_id: [] for node_id in genome.node_gene_by_node_id}
        for connection in genome.connection_by_innovation_id.values(): 
            if connection.enabled:
                G[connection.in_node].append(connection.out_node)
                
        return G 

    @staticmethod
    def __create_inverted_graph(genome: Genome) -> dict[int, list[tuple[int, float]]]:
        """ to -> [(from, val)], only if from -> to enabled """
        
        G_inverted: dict[int, list[tuple[int, float]]] = {node_id: [] for node_id in genome.node_gene_by_node_id}
        for connection in genome.connection_by_innovation_id.values():
            if connection.enabled:
                G_inverted[connection.out_node].append((connection.in_node, connection.weight))
                
        return G_inverted

    @staticmethod
    def __sort_topologically(G: dict[int, list[int]], G_inverted: dict[int, list[tuple[int, float]]]) -> list[int]:
        in_size: dict[int, int] = {}
        q: deque[int] = deque()
        evaluation_order: list[int] = []
        
        for to, from_tuples in G_inverted.items():
            in_size[to] = len(from_tuples)
            if len(from_tuples) == 0:
                q.append(to)
                
        while q: 
            node_id = q.popleft()
            evaluation_order.append(node_id) 
            
            for to_node_id in G[node_id]:
                in_size[to_node_id] -= 1 
                if in_size[to_node_id] == 0: 
                    q.append(to_node_id)
        
        assert len(G) == len(evaluation_order), "error: there is a cycle"
        return evaluation_order

    def predict(self, observations: list[float]) -> list[float]:
        assert len(observations) == len(self.input_ids), "wrong number of observations"
        
        values: dict[int, float] = dict(zip(self.input_ids, observations))
        values[self.bias_id] = 1.0

        for node_id in self.evaluation_order:
            total = sum(values[source_id] * weight for source_id, weight in self.G_inverted[node_id])
            values[node_id] = self._sigmoid(total)

        return [values[output_id] for output_id in self.output_ids]

    @staticmethod
    def _sigmoid(x: float) -> float:
        z = max(-60.0, min(60.0, SIGMOID_STEEPNESS * x)) # clamp to avoid oerflow in exp 
        return 1.0 / (1.0 + math.exp(-z))
