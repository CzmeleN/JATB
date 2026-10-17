from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from jatb.bot.policy import IPolicy

@dataclass
class EpisodeResult:
    policy_index: int
    fitness: float
    total_reward: float
    steps: int


@dataclass
class Transition:
    state: list[float]
    action: int
    reward: float
    next_state: list[float]
    done: bool


class IScheduler(ABC):
    def __init__(self, num_parallel: int, base_port: int = 8450, episodes_per_policy: int = 1) -> None:
        self.num_parallel = num_parallel
        self.base_port = base_port
        self.episodes_per_policy = episodes_per_policy

    @abstractmethod
    def run_episodes(self, policies: Sequence[IPolicy]) -> list[EpisodeResult]: ...

    @abstractmethod
    def collect_steps(
        self,
        action_selector: Callable[[list[float]], int],
        num_steps: int,
    ) -> list[Transition]: ...

    # shut down all games
    @abstractmethod
    def close(self) -> None: ...
