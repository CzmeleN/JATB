from queue import Queue
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor

from jatb.policy import IPolicy
from jatb.game import Game
from jatb.game.reward_function import IRewardFunction
from jatb.io import IInputHandler, IOutputHandler
from .Ischeduler import IScheduler
from .results import GameResult, Transition


class Scheduler(IScheduler):
    """
    Keeps a pool of num_instances TMNF instances
    """

    def __init__(self,
                 reward_function: IRewardFunction,
                 input_handler: IInputHandler,
                 output_handler: IOutputHandler,
                 map_name: str,
                 num_instances: int = 1,
                 base_port: int = 8450,
                 max_race_time_ms: int = 10_000,
                 start_cmds: Sequence[str] = ()) -> None:
        if num_instances < 1:
            raise ValueError("num_instances must be >= 1")

        self._input_handler = input_handler
        self._output_handler = output_handler

        self._games: list[Game] = [
            Game(reward_function,
                 input_handler,
                 output_handler,
                 map_name,
                 max_race_time_ms=max_race_time_ms,
                 port=base_port + i,
                 start_cmds=list(start_cmds))
            for i in range(num_instances)
        ]

        self._free_instances: Queue[Game] = Queue()
        self._executor = ThreadPoolExecutor(max_workers=num_instances,
                                            thread_name_prefix="jatb-instance")
        self._launched = False

    def run_games(self, policies: Sequence[IPolicy]) -> Sequence[GameResult]:
        self._launch()

        return list(self._executor.map(self._run_on_free_instance, policies))

    def collect_steps(self, policy: IPolicy, num_steps: int) -> list[Transition]:
        # TODO fill after/while implementing DQN
        raise NotImplementedError("DQN not implemented")

    def get_input_size(self) -> int:
        return self._input_handler.get_input_size()

    def get_output_size(self) -> int:
        return self._output_handler.get_output_size()

    def close_games(self) -> None:
        for game in self._games:
            game.close()

    def _launch(self) -> None:
        """ starts all TMNF instances parallelly :w """
        if self._launched:
            return

        list(self._executor.map(lambda g: g.launch(), self._games))

        for game in self._games:
            self._free_instances.put(game)

        self._launched = True

    def _run_on_free_instance(self, policy: IPolicy) -> GameResult:
        game = self._free_instances.get()

        try:
            return self._play_episode(game, policy)
        finally:
            self._free_instances.put(game)

    @staticmethod
    def _play_episode(game: Game, policy: IPolicy) -> GameResult:
        game.reset()
        total_reward = 0.0
        steps = 0

        while not game.is_finished:
            observations = game.get_observations()
            step = game.make_step(policy.predict(observations))
            total_reward += step.reward
            steps += 1

        reached_finish = game.prev_game_state.get_is_finished()

        return GameResult(total_reward, steps, reached_finish)
