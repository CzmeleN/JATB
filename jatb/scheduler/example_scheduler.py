import select
import sys
from collections import deque
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from jatb.bot.policy import IPolicy
from jatb.scheduler.game_instance import GameInstance
from jatb.scheduler.scheduler import EpisodeResult, IScheduler, Transition

@dataclass
class _Episode:
    policy_index: int
    connected: bool = False  # False while the game is still loading
    race_time: int = 0

# At most num_parallel games run at once, each on its own port. Every episode runs on a freshly launched game:
# when it ends, the game is closed and a new one is launched on the same port for the next pending episode.
# At the start all num_parallel games load at the same time, which is the heaviest moment for the CPU,
# so keep num_parallel small.
#
# Relaunching is temporary: the plugin can't reset the race yet. Once it can (Respawn / RewindToState),
# games should be launched once and reset between episodes, since a launch takes about a dozen seconds
# while episodes are much shorter.
class ExampleScheduler(IScheduler):
    def __init__(
        self,
        num_parallel: int,
        base_port: int = 8450,
        episodes_per_policy: int = 1,
        episode_ms: int = 5000,
    ) -> None:
        super().__init__(num_parallel, base_port, episodes_per_policy)
        self.episode_ms = episode_ms
        # one game per port, relaunched on the same port for every episode
        self.game_pool = [GameInstance(i, base_port + i) for i in range(num_parallel)]

    def run_episodes(self, policies: Sequence[IPolicy]) -> list[EpisodeResult]:
        pending = deque(i for i in range(len(policies)) for _ in range(self.episodes_per_policy))
        active: dict[GameInstance, _Episode] = {}  # game -> episode running on it
        results: list[EpisodeResult] = []

        for game in self.game_pool:
            if not pending:
                break
            game.start_process()
            active[game] = _Episode(pending.popleft())

        while active:
            for game, episode in active.items():
                if not episode.connected:
                    # non-blocking connection try
                    episode.connected = game.try_connect()
                    if episode.connected:
                        # the game starts in the menu and the plugin only sends frames during a race
                        print(f"game {game.index} (port {game.port}): start a race to begin the episode", file=sys.stderr)

            # wait up to 0.5 s for a frame from any connected game and read only the games that sent one,
            # so a game sitting in the menu doesn't stop the others; with no connected game it just waits,
            # so the loop doesn't spin on try_connect() while the games are loading
            connected = {game.comm: game for game, episode in active.items() if episode.connected}
            ready, _, _ = select.select(list(connected), [], [], 0.5)

            for comm in ready:
                game = connected[comm]
                episode = active[game]
                frame = comm.recv_frame()
                episode.race_time = frame.raceTime
                # TODO: send policies[episode.policy_index] action once the plugin accepts actions

                if episode.race_time < self.episode_ms:
                    # episode is not finished yet
                    continue

                # TODO: fill with correct data
                results.append(EpisodeResult(episode.policy_index, fitness=0.0, total_reward=0.0, steps=0))
                print(f"game {game.index} (port {game.port}): policy {episode.policy_index} finished at {episode.race_time} ms", file=sys.stderr)

                # TODO: swap close for reset (details above the class)
                game.close()

                if pending:
                    game.start_process()
                    active[game] = _Episode(pending.popleft())
                else:
                    del active[game]

        return results

    # TODO: needs actions sent to the plugin
    def collect_steps(
        self,
        action_selector: Callable[[list[float]], int],
        num_steps: int,
    ) -> list[Transition]:
        raise NotImplementedError

    def close(self) -> None:
        for game in self.game_pool:
            game.close()
