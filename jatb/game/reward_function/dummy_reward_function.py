from jatb.game.reward_function import IRewardFunction
from jatb.trackmania_interface.game_state import GameState

class DummyRewardFunction(IRewardFunction):
    def compute(self, prev_state: GameState, state: GameState) -> float:
        return 0.0