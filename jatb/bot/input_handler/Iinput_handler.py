from abc import ABC, abstractmethod
from jatb.trackmania_interface import GameState

class IInputHandler(ABC):
    @abstractmethod
    def _normalise_input(self, input_values: list[float]) -> list[float]: ...

    @abstractmethod
    def _get_input_from_game_state(self, game_state: GameState) -> list[float]: ...
    
    @abstractmethod
    def get_input_size(self) -> int: ...

    def get_input(self, game_state: GameState) -> list[float]:
        return self._normalise_input(self._get_input_from_game_state(game_state))