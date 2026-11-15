from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from jatb.policy import IPolicy


@dataclass
class GameResult:
    """ 
        use for NEAT
        steps and finished are mostly for debug info 
        finished is true if bot has reached end line
    """
    
    total_reward: float
    steps: int 
    finished: bool

@dataclass
class Transition:
    """ 
        use for DQN
        finished is true if bot has reached end line
    """
    
    state: list[float] # TODO we could add later Istate related to output_handel
    action: int
    reward: float
    next_state: list[float]
    finished: bool
    done: bool

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