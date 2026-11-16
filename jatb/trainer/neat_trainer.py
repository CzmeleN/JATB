import random

from jatb.neat import ConnectionGene, Genome, InnovationTracker, NodeGene, NodeType
from jatb.scheduler import IScheduler, GameResult
from .Itrainer import ITrainer
from tqdm import tqdm
from ..policy import NeatPolicy
from collections.abc import Sequence


class NeatTrainer(ITrainer):
    
    def __save_training(self) -> None:
        pass 
    
    def __try_load_training(self, continue_training: bool, load_path: str) -> None: 
        pass
    
    def __create_policies(self) -> Sequence[NeatPolicy]:
        pass
    
    def __create_initial_genome(self) -> Genome:
        genome = Genome()
        for node in self.nodes:
            genome.add_node(node)

        for in_node in self.source_ids:
            for out_node in self.output_ids:
                genome.add_connection(ConnectionGene(
                    in_node=in_node,
                    out_node=out_node,
                    weight=random.uniform(-1.0, 1.0),
                    enabled=True,
                    innovation=self.tracker.get_innovation(in_node, out_node),
                ))
        return genome

    def __create_initial_genomes(self, num_inputs: int, num_outputs: int) -> list[Genome]: 
        input_ids = [self.tracker.new_node_id() for _ in range(num_inputs)]
        self.bias_id = self.tracker.new_node_id()
        self.output_ids = [self.tracker.new_node_id() for _ in range(num_outputs)]
        self.source_ids = input_ids + [self.bias_id]

        self.nodes = (
            [NodeGene(i, NodeType.INPUT) for i in input_ids]
            + [NodeGene(self.bias_id, NodeType.BIAS)]
            + [NodeGene(o, NodeType.OUTPUT) for o in self.output_ids]
        )

        # prealocate innovations
        for in_node in self.source_ids:
            for out_node in self.output_ids:
                self.tracker.create_innovation(in_node, out_node)

        return [self.__create_initial_genome() for _ in range(self.population_size)]
    
    def __load_genomes(self, continue_training: bool, load_path: str) -> None:
        self.genomes: list[Genome] = []
        self.__try_load_training(continue_training, load_path)
        
        if self.genomes == []: 
            self.population_size: int = 150
            self.tracker: InnovationTracker = InnovationTracker()
            self.genomes = self.__create_initial_genomes(self.scheduler.get_input_size(), self.scheduler.get_output_size())
    
    def __init__(self,
                 scheduler: IScheduler,
                 epochs: int,
                 save_path: str,
                 continue_training: bool, 
                 load_path: str
                 ) -> None:
        super().__init__(scheduler)
        self.epochs: int = epochs 
        self.save_path: str = save_path
        self.__load_genomes(continue_training, load_path)
    
    def train(self) -> None:
        for _ in tqdm(range(self.epochs)):
            policies = self.__create_policies() 
            results: Sequence[GameResult] = self.scheduler.run_games(policies)