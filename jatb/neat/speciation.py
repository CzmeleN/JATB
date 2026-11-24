import math
import random 
from dataclasses import dataclass, field
from .genome import Genome

@dataclass 
class Species:
    id: int 
    representative: Genome 
    member_ids: list[int] = field(default_factory=list)
    best_fitness: float = -math.inf
    generations_without_improvement: int = 0 
    
@dataclass(frozen=True)
class SpeciationConfig: 
    excess_coefficient: float = 1.0
    disjoint_coefficient: float = 1.0 
    weight_coeffictine: float = 0.4
    default_compatibility_threshold: float = 3.0 
    small_genemo_size: int = 20 
    target_species_count: int = 10 
    threshold_step: float = 0.05 
    min_threshold: float = 0.1
    max_stagnation: int = 15

class Speciation: 
    def __init__(self,
                 config: SpeciationConfig | None = None,
                 rng: random.Random | None = None) -> None:
        self.config: SpeciationConfig = config if config is not None else SpeciationConfig() 
        self.rng: random.Random = rng if rng is not None else random.Random()
        self.all_species: list[Species] = []
        self._next_species_id: int = 0 
        self._compatibility_threshold = self.config.default_compatibility_threshold
        
    def __call__(self, genomes: list[Genome], fitnesses: list[float], population_size: int) -> tuple[list[Species], dict[int, int]]:
        """
            returns:
                * all_species 
                * species id -> number of children
        """
        
        self._speciate(genomes)
        self._adjust_threshold() 
        self._update_stagnation(fitnesses)
        adjusted_fitnesses = self._adjust_fitnesses(fitnesses)
        offsprint_counts = self._offspring_counts(fitnesses, adjusted_fitnesses, population_size)
        return self.all_species, offsprint_counts
        
    def _speciate(self, genomes: list[Genome]) -> None:
        for species in self.all_species:
            species.member_ids = []
            
        for genome_id, genome in enumerate(genomes):
            species = self._try_find_species(genome)
            if species is None: 
                species = Species(self._next_species_id, genome)
                self._next_species_id += 1
                self.all_species.append(species)
            species.member_ids.append(genome_id)
            
        self.all_species = [s for s in self.all_species if s.member_ids]
        for species in self.all_species:
            species.representative = genomes[self.rng.choice(species.member_ids)]
        
    def _update_stagnation(self, fitnesses: list[float]) -> None: 
        for species in self.all_species:
            best = max(fitnesses[i] for i in species.member_ids)
            if best > species.best_fitness:
                species.best_fitness = best 
                species.generations_without_improvement = 0
            else: 
                species.generations_without_improvement += 1
                
    def _adjust_fitnesses(self, fitnesses: list[float]) -> list[float]:
        lowest_fitness = min(fitnesses)
        adjusted_fitnesses =[0.0] * len(fitnesses)
        for species in self.all_species: 
            size = len(species.member_ids)
            for genome_id in species.member_ids:
                adjusted_fitnesses[genome_id] = (fitnesses[genome_id] - lowest_fitness) / size
        return adjusted_fitnesses
                
    def _offspring_counts(self, fitnesses: list[float], adjusted_fitnesses: list[float], population_size: int) -> dict[int, int]:
        """species id -> number of children"""
        
        best_genome_id = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
        allowed_species_to_reproduce = [s for s in self.all_species
                   if s.generations_without_improvement <= self.config.max_stagnation 
                   or best_genome_id in s.member_ids]
        
        species_adjusted_fitness_sum = {s.id: sum(adjusted_fitnesses[i] for i in s.member_ids) for s in allowed_species_to_reproduce} 
        total = sum(species_adjusted_fitness_sum.values())
        if total == 0: 
            species_adjusted_fitness_sum = {s.id: float(len(s.member_ids)) for s in allowed_species_to_reproduce} 
            total = float(sum(species_adjusted_fitness_sum.values()))
            
        exact = {s_id: population_size * value / total for s_id, value in species_adjusted_fitness_sum.items()}
        offspring_counts = {s_id: math.floor(value) for s_id, value in exact.items()}
 
        missing = population_size - sum(offspring_counts.values())
        for s_id in sorted(exact, key=lambda s_id: exact[s_id] - offspring_counts[s_id], reverse=True)[:missing]:
            offspring_counts[s_id] += 1
        
        for species in self.all_species:
            offspring_counts.setdefault(species.id, 0)
        return offspring_counts
    
    def _adjust_threshold(self) -> None: 
        if len(self.all_species) > self.config.target_species_count:
            self._compatibility_threshold += self.config.threshold_step
        elif len(self.all_species) < self.config.target_species_count:
            self._compatibility_threshold = max(self.config.min_threshold, 
                                                      self._compatibility_threshold - self.config.threshold_step)
    
    def _distance(self, genome_a: Genome, genome_b: Genome) -> float:
        genes_a = genome_a.connection_by_innovation_id
        genes_b = genome_b.connection_by_innovation_id
        if not genes_a and not genes_b:
            return 0.0 
        
        max_a_connection_id = max(genes_a, default=-1)
        max_b_connection_id = max(genes_b, default=-1)
        
        excess = disjoint = 0 
        for innovation in genes_a.keys() ^ genes_b.keys():
            other_max_connection_id = max_b_connection_id if innovation in genes_a else max_a_connection_id
            if innovation > other_max_connection_id:
                excess += 1 
            else:
                disjoint += 1
                
        matching = genes_a.keys() & genes_b.keys()
        weight_diff = (sum(abs(genes_a[i].weight - genes_b[i].weight) for i in matching) / len(matching) if matching else 0.0)
        
        n = max(len(genes_a), len(genes_b))
        if n < self.config.small_genemo_size:
            n = 1
            
        return (self.config.excess_coefficient * excess / n
                + self.config.disjoint_coefficient * disjoint / n 
                + self.config.weight_coeffictine * weight_diff)
    
    def _try_find_species(self, genome: Genome) -> Species | None: 
        for species in self.all_species:
            if self._distance(genome, species.representative) < self._compatibility_threshold:
                return species
        return None