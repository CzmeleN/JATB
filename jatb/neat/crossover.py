import random
from dataclasses import dataclass
from .genome import ConnectionGene, Genome, NodeType
from .utils import edge_creates_cycle

@dataclass(frozen=True)
class CrossoverConfig:
    disable_gene_prob: float = 0.75 
    non_matching_gene_inherit_prob_on_tie: float = 0.5
    
class Crossover:
    def __init__(self,
                 config: CrossoverConfig = CrossoverConfig(),
                 rng: random.Random | None = None) -> None:
        self.config: CrossoverConfig = config 
        self.rng: random.Random = rng if rng is not None else random.Random()
    
    def __call__(self, parent_a: Genome, fitness_a: float, parent_b: Genome, fitness_b: float) -> Genome:
        self.fitter_parent, self.weaker_parent, equal_fitness = self._order_by_fitness(parent_a, fitness_a, parent_b, fitness_b)
        self.genes_f = self.fitter_parent.connection_by_innovation_id
        self.genes_w = self.weaker_parent.connection_by_innovation_id
        
        self.child = self._create_child_with_fixed_nodes()
        self._inherit_matching_genes()
        
        if equal_fitness:
            self._inherit_disjoint_and_excess_genes_randomly()
        else:
            self._inherit_disjoint_and_excess_genes_from_fitter()
        
        return self.child
            
    def _inherit_disjoint_and_excess_genes_from_fitter(self) -> None:
        for innovation in sorted(self.genes_f.keys() - self.genes_w.keys()):
            gene = self.genes_f[innovation]
            self._inherit_gene(gene, not gene.enabled)
            
    def _inherit_disjoint_and_excess_genes_randomly(self) -> None:
        genes_only_in_one = [self.genes_f[i] for i in self.genes_f.keys() - self.genes_w.keys()] \
                          + [self.genes_w[i] for i in self.genes_w.keys() - self.genes_f.keys()]
        genes_only_in_one.sort(key=lambda gene: gene.innovation)
        
        for gene in genes_only_in_one:
            if self.rng.random() >= self.config.non_matching_gene_inherit_prob_on_tie:
                continue
            if edge_creates_cycle(self.child, (gene.in_node, gene.out_node)):
                continue
            self._inherit_gene(gene, not gene.enabled)

    def _inherit_matching_genes(self) -> None:
        for innovation in sorted(self.genes_f.keys() & self.genes_w.keys()):
            gene_f, gene_w = self.genes_f[innovation], self.genes_w[innovation]
            chosen = self.rng.choice((gene_f, gene_w))
            is_disabled_in_parent = not gene_f.enabled or not gene_w.enabled
            self._inherit_gene(chosen, is_disabled_in_parent)
            
    def _inherit_gene(self, gene: ConnectionGene, is_disabled_in_parent: bool,) -> None:
        self._add_missing_nodes_required_to_create_connection(gene)
        self.child.add_connection(ConnectionGene(
            in_node=gene.in_node,
            out_node=gene.out_node,
            weight=gene.weight,
            enabled=self._child_gene_enabled(is_disabled_in_parent),
            innovation=gene.innovation,
        ))
        
    def _add_missing_nodes_required_to_create_connection(self, gene: ConnectionGene) -> None:
        for node_id in (gene.in_node, gene.out_node):
            if node_id in self.child.node_gene_by_node_id:
                continue
            node = self.fitter_parent.node_gene_by_node_id.get(node_id) or self.weaker_parent.node_gene_by_node_id[node_id]
            self.child.add_node(node)
    
    def _child_gene_enabled(self, is_disabled_in_parent: bool) -> bool: 
        if not is_disabled_in_parent:
            return True 
        return self.rng.random() >= self.config.disable_gene_prob
    
    def _create_child_with_fixed_nodes(self) -> Genome:
        child = Genome()
        for node in self.fitter_parent.node_gene_by_node_id.values():
            if node.type != NodeType.HIDDEN:
                child.add_node(node)
                
        return child
    
    @staticmethod
    def _order_by_fitness(parent_a: Genome, fitness_a: float, parent_b: Genome, fitness_b: float) -> tuple[Genome, Genome, bool]:
        """ [fitter parent, less fit parent, equal_fitness] """
        if fitness_b > fitness_a:
            return parent_b, parent_a, False
        return parent_a, parent_b, fitness_a == fitness_b
    