from abc import ABC, abstractmethod
from collections.abc import Sequence
from jatb.policy import IPolicy
from .results import GameResult, Transition


class IScheduler(ABC):
    @abstractmethod
    def run_games(self, policies: Sequence[IPolicy]) -> Sequence[GameResult]: ...
        # TODO should return output in the same order as input

    @abstractmethod
    def collect_steps(
        self,
        policy: IPolicy,
        num_steps: int,
    ) -> list[Transition]: ...
    
    @abstractmethod
    def get_input_size(self) -> int: ... 
    
    @abstractmethod
    def get_output_size(self) -> int: ...
