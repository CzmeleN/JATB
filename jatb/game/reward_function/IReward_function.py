from abc import ABC, abstractmethod
from jatb.trackmania_interface.game_state import GameState

class IRewardFunction(ABC):
    @abstractmethod
    def compute(self, prev_state: GameState, state: GameState) -> float: ...