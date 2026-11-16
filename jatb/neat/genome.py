from dataclasses import asdict, dataclass
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
        self.node_gene_by_node_id: dict[int, NodeGene] = {}
        self.connection_by_innovation_id: dict[int, ConnectionGene] = {}

    def add_node(self, node: NodeGene) -> None:
        self.node_gene_by_node_id[node.id] = node

    def add_connection(self, connection: ConnectionGene) -> None:
        self.connection_by_innovation_id[connection.innovation] = connection
        
    def to_dict(self) -> dict:
        return {
            "nodes": [{"id": node.id, "type": node.type.value} for node in self.node_gene_by_node_id.values()],
            "connections": [asdict(connection) for connection in self.connection_by_innovation_id.values()],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Genome":
        genome = cls()
        for node in data["nodes"]:
            genome.add_node(NodeGene(node["id"], NodeType(node["type"])))
        for connection in data["connections"]:
            genome.add_connection(ConnectionGene(**connection))
        return genome
