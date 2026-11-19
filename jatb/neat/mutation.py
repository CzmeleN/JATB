import random 
from dataclasses import dataclass
from .genome import ConnectionGene, Genome, NodeGene, NodeType
from .innovation_tracker import InnovationTracker
from .utils import edge_creates_cycle

@dataclass(frozen=True)
class MutationConfig:
    """
        pertub - small change in weight insetead of assigning a new random value
        weight_init_range -  new weights ~ uniform(-range, range)
        add_connnection_attempts - random tries to find an acyclic edge
    """
    weight_mutate_prob: float = 0.8
    weight_perturb_prob: float = 0.9
    weight_perturb_power: float = 0.5
    weight_init_range: float = 1.0
    weight_clamp: float = 8.0
    add_connection_prob: float = 0.05
    add_node_prob: float = 0.03
    add_connection_attempts: int = 20
    
class Mutator:
    def __init__(self, 
                 tracker: InnovationTracker, 
                 config: MutationConfig = MutationConfig(),
                 rng: random.Random | None = None):
        self.tracker: InnovationTracker = tracker 
        self.config: MutationConfig = config 
        self.rng: random.Random = rng if rng is not None else random.Random()
    
    def mutate_genome_inplace(self, genome: Genome) -> None:
        if self.rng.random() < self.config.weight_mutate_prob:
            self._mutate_weights_inplace(genome)
        if self.rng.random() < self.config.add_connection_prob:
            self._mutate_add_connection_inplace(genome)
        if self.rng.random() < self.config.add_node_prob:
            self._mutate_add_node_inplace(genome)
        
    def _mutate_add_connection_inplace(self, genome: Genome) -> None: 
        nodes = genome.node_gene_by_node_id.values()
        sources = [n.id for n in nodes if n.type != NodeType.OUTPUT]
        targets = [n.id for n in nodes if n.type in (NodeType.HIDDEN, NodeType.OUTPUT)] 
        existing_edges = {(c.in_node, c.out_node) for c in genome.connection_by_innovation_id.values()}
        
        for _ in range(self.config.add_connection_attempts):
            edge = (self.rng.choice(sources), self.rng.choice(targets))
            
            if edge[0] == edge[1]:
                continue
            if edge in existing_edges:
                continue
            if edge_creates_cycle(genome, edge):
                continue 
            
            genome.add_connection(ConnectionGene(
                in_node=edge[0],
                out_node=edge[1],
                weight=self.rng.uniform(-self.config.weight_init_range, self.config.weight_init_range),
                enabled=True,
                innovation=self.tracker.get_or_create_innovation(*edge),
            ))
            
            break

    def _mutate_add_node_inplace(self, genome: Genome) -> None: 
        candidates = [c for c in genome.connection_by_innovation_id.values() if c.enabled]
        self.rng.shuffle(candidates)
        
        for connection in candidates:
            node_id = self.tracker.get_or_create_split_node_id(connection.innovation) 
            if node_id in genome.node_gene_by_node_id:
                continue # this genome already split this connection 
            
            connection.enabled = False
            genome.add_node(NodeGene(node_id, NodeType.HIDDEN))
            
            genome.add_connection(ConnectionGene(
                in_node=connection.in_node,
                out_node=node_id,
                weight=1.0,
                enabled=True,
                innovation=self.tracker.get_or_create_innovation(connection.in_node, node_id)
            ))
            genome.add_connection(ConnectionGene(
                in_node=node_id,
                out_node=connection.out_node,
                weight=connection.weight,
                enabled=True, 
                innovation=self.tracker.get_or_create_innovation(node_id, connection.out_node)
            ))
            
            break
    
    def _mutate_weights_inplace(self, genome: Genome) -> None: 
        for connection in genome.connection_by_innovation_id.values():
            if self.rng.random() < self.config.weight_perturb_prob:
                connection.weight += self.rng.uniform(-self.config.weight_perturb_power, self.config.weight_perturb_power)
            else: 
                connection.weight = self.rng.uniform(-self.config.weight_init_range, self.config.weight_init_range)
                
            connection.weight = max(-self.config.weight_clamp, min(self.config.weight_clamp, connection.weight)) 