""" 
    TODO: 
        * 
    
"""

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
        self.__try_load_training(continue_training, load_path)
    
    def train(self) -> None:
        for _ in tqdm(range(self.epochs)):
            policies = self.__create_policies() 
            results: Sequence[GameResult] = self.scheduler.run_games(policies)