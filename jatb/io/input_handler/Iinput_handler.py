from abc import ABC, abstractmethod
from jatb.trackmania_interface import GameState

class IInputHandler(ABC):
    @abstractmethod
    def get_input_size(self) -> int: ...

    @abstractmethod
    def get_input(self, game_state: GameState) -> list[float]: ...