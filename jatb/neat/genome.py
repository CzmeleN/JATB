from dataclasses import dataclass, field
from enum import Enum


class NodeType(Enum):
    INPUT = "input"
    BIAS = "bias"
    OUTPUT = "output"
    HIDDEN = "hidden"

@dataclass(frozen=True)
class NodeGene:
    id: int
    type: NodeType

@dataclass
class ConnectionGene:
    in_node: int
    out_node: int
    weight: float
    enabled: bool
    innovation: int

class Genome:
    def __init__(self) -> None:
        self.nodes: dict[int, NodeGene] = {}
        self.connections: dict[int, ConnectionGene] = {}

    def add_node(self, node: NodeGene) -> None:
        self.nodes[node.id] = node

    def add_connection(self, connection: ConnectionGene) -> None:
        self.connections[connection.innovation] = connection