import math 
import random
from dataclasses import dataclass
from .genome import Genome
from .speciation import Species
from .crossover import Crossover
from .mutation import Mutator
from .innovation_tracker import InnovationTracker

@dataclass(frozen=True)
class ReproductionConfig:
    """
        elitism_min_species_size - species bigger than this keep their champion unchanged
    """
    survival_rate: float = 0.2 
    elitism_min_species_size: int = 5 
    no_crossover_prob: float = 0.25
    interspecies_mating_prob: float = 0.001
    
class Reproducer:
    def __init__(self,
                 tracker: InnovationTracker,
                 config: ReproductionConfig | None = None,
                 rng: random.Random | None = None) -> None:
        self.config = config if config is not None else ReproductionConfig() 
        self.rng = rng if rng is not None else random.Random()
        
        self.crossover = Crossover(rng=self.rng)
        self.mutator = Mutator(tracker, rng=self.rng)
    
    def __call__(self, genomes: list[Genome], all_species: list[Species], offspring_count: dict[int, int], fitnesses: list[float], population_size: int) -> list[Genome]:
        new_genomes: list[Genome] = []
        
        for species in all_species:
            count = offspring_count[species.id]
            if count == 0:
                continue 
            
            ranked_genome_ids = sorted(species.member_ids, key=lambda i: fitnesses[i], reverse=True)
            if len(ranked_genome_ids) > self.config.elitism_min_species_size:
                new_genomes.append(genomes[ranked_genome_ids[0]].copy())
                count -= 1
                
            parents_ids = ranked_genome_ids[:max(1, math.ceil(len(ranked_genome_ids) * self.config.survival_rate))]
            for _ in range(count):
                new_genomes.append(self._make_child(genomes, parents_ids, all_species, fitnesses))
        
        assert len(new_genomes) == population_size 
        return new_genomes
    
    def _make_child(self, genomes: list[Genome], parents: list[int], all_species: list[Species], fitnesses: list[float]) -> Genome:
        parent_a_id = self.rng.choice(parents)
        
        if self.rng.random() < self.config.interspecies_mating_prob and len(all_species) > 1:
            other_species = self.rng.choice(all_species)
            parent_b_id = max(other_species.member_ids, key=lambda i: fitnesses[i])
            child = self.crossover(genomes[parent_a_id], fitnesses[parent_a_id], 
                                   genomes[parent_b_id], fitnesses[parent_b_id])
        elif len(parents) == 1 or self.rng.random() < self.config.no_crossover_prob:
            child = genomes[parent_a_id].copy()
        else:
            parent_b_id = self.rng.choice([p for p in parents if p != parent_a_id])
            child = self.crossover(genomes[parent_a_id], fitnesses[parent_a_id], 
                                   genomes[parent_b_id], fitnesses[parent_b_id])
            
        self.mutator.mutate_genome_inplace(child)
        return child