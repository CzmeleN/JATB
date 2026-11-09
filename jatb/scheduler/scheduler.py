from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from jatb.policy import IPolicy

@dataclass
class GameResult:
    total_reward: float
    steps: int
    finished: bool

@dataclass
class Transition:
    state: list[float]
    action: int
    reward: float
    next_state: list[float]
    finished: bool
    done: bool


class IScheduler(ABC):
    @abstractmethod
    def run_games(self, policies: Sequence[IPolicy]) -> Sequence[GameResult]: ...

    @abstractmethod
    def collect_steps(
        self,
        policy: IPolicy,
        num_steps: int,
    ) -> list[Transition]: ...