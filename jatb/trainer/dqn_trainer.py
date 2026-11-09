from jatb.scheduler import IScheduler
from jatb.trainer.dqn_agent import DQNAgent
from jatb.trainer.Itrainer import ITrainer
from jatb.trainer.replay_memory import ReplayMemory

class DQNTrainer(ITrainer):
    def __init__(
        self,
        scheduler: IScheduler,
        num_iterations: int = 100,
        steps_per_collect: int = 200,
        updates_per_collect: int = 1,
        batch_size: int = 64,
        n_actions: int = 6,
        n_observations: int = 18,
        buffer_capacity: int = 1000
    ) -> None:
        super().__init__(scheduler)
        self.n_actions = n_actions
        self.n_observations = n_observations
        self.agent = DQNAgent(n_observations, n_actions)
        self.replay_buffer = ReplayMemory(buffer_capacity)
        self.num_iterations = num_iterations
        self.steps_per_collect = steps_per_collect
        self.updates_per_collect = updates_per_collect
        self.batch_size = batch_size

    def train(self) -> None:
        for _ in range(self.num_iterations):
            transitions = self.scheduler.collect_steps(self.agent.policy, num_steps=self.steps_per_collect)
            self.replay_buffer.extend(transitions)

            # warmup: don't learn until the buffer holds at least one batch
            if len(self.replay_buffer) < self.batch_size:
                continue

            for _ in range(self.updates_per_collect):
                batch = self.replay_buffer.sample(self.batch_size)
                self.agent.update(batch)
