import json
import os
import random

from jatb.neat import ConnectionGene, Genome, InnovationTracker, NodeGene, NodeType
from jatb.scheduler import IScheduler, GameResult
from .Itrainer import ITrainer
from tqdm import tqdm
from ..policy import NeatPolicy
from collections.abc import Sequence


class NeatTrainer(ITrainer):
    def __del__(self):
        self.__save_training() 
    
    def __save_training(self) -> None:
        data = {
            "population_size": self.population_size,
            "tracker": self.tracker.to_dict(),
            "genomes": [genome.to_dict() for genome in self.genomes],
        }
        with open(self.save_path, "w") as f:
            json.dump(data, f)
    
    def __try_load_training(self, continue_training: bool, load_path: str) -> None: 
        if not continue_training or not os.path.exists(load_path):
            return

        with open(load_path) as f:
            data = json.load(f)

        self.population_size = data["population_size"]
        self.tracker = InnovationTracker.from_dict(data["tracker"])
        self.genomes = [Genome.from_dict(genome) for genome in data["genomes"]]
        self.__restore_node_ids()

    def __restore_node_ids(self) -> None:
        nodes = self.genomes[0].node_gene_by_node_id.values() 
        
        self.input_ids = sorted(n.id for n in nodes if n.type == NodeType.INPUT)
        self.bias_id = next(n.id for n in nodes if n.type == NodeType.BIAS)
        self.output_ids = sorted(n.id for n in nodes if n.type == NodeType.OUTPUT)
        self.source_ids = self.input_ids + [self.bias_id]
    
    def __create_policies(self) -> Sequence[NeatPolicy]:
        pass
    
    def __create_initial_genome(self, nodes: list[NodeGene]) -> Genome:
        genome = Genome()
        for node in nodes:
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
        self.input_ids = [self.tracker.new_node_id() for _ in range(num_inputs)]
        self.bias_id = self.tracker.new_node_id()
        self.output_ids = [self.tracker.new_node_id() for _ in range(num_outputs)]
        self.source_ids = self.input_ids + [self.bias_id]

        nodes = (
            [NodeGene(i, NodeType.INPUT) for i in self.input_ids]
            + [NodeGene(self.bias_id, NodeType.BIAS)]
            + [NodeGene(o, NodeType.OUTPUT) for o in self.output_ids]
        )

        # prealocate innovations
        for in_node in self.source_ids:
            for out_node in self.output_ids:
                self.tracker.create_innovation(in_node, out_node)

        return [self.__create_initial_genome(nodes) for _ in range(self.population_size)]
    
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