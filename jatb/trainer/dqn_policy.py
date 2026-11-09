import math
import random

import torch

from jatb.policy import IPolicy
from jatb.trainer.dqn_net import DQN

class DQNGreedyPolicy(IPolicy):
    def __init__(
        self,
        output_size: int,
        net: DQN,
        eps_start: float = 0.9,
        eps_end: float = 0.01,
        eps_decay: float = 2500,
        device: torch.device | None = None
    ) -> None:
        self.output_size = output_size
        self.net = net
        self.steps_done = 0
        self.eps_start = eps_start
        self.eps_end = eps_end
        self.eps_decay = eps_decay
        self.device = device

    def epsilon(self) -> float:
        return self.eps_end + (self.eps_start - self.eps_end) * math.exp(-1.0 * self.steps_done / self.eps_decay)

    def predict(self, observations: list[float]) -> list[float]:
        eps = self.epsilon()
        self.steps_done += 1
        if random.random() < eps:
            return [random.random() for _ in range(self.output_size)]

        with torch.no_grad():
            input = torch.tensor(observations, dtype=torch.float32, device=self.device).unsqueeze(0)
            return self.net(input).squeeze(0).tolist()
