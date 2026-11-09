import torch
import torch.nn as nn
import torch.optim as optim

from jatb.scheduler import Transition
from jatb.trainer.dqn_net import DQN
from jatb.trainer.dqn_policy import DQNGreedyPolicy

class DQNAgent:
    def __init__(
        self,
        n_observations: int,
        n_actions: int,
        gamma: float = 0.99,
        lr: float = 3e-4,
        device: torch.device | None = None,
    ) -> None:
        self.n_actions = n_actions
        self.gamma = gamma
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.net = DQN(n_observations, n_actions).to(self.device)
        self.policy = DQNGreedyPolicy(n_actions, self.net, device=self.device)
        self.optimizer = optim.AdamW(self.net.parameters(), lr=lr, amsgrad=True)

    def update(self, batch: list[Transition]) -> None:
        states = torch.tensor([t.state for t in batch], dtype=torch.float32, device=self.device)
        actions = torch.tensor([t.action for t in batch], dtype=torch.long, device=self.device).unsqueeze(1)
        rewards = torch.tensor([t.reward for t in batch], dtype=torch.float32, device=self.device)
        next_states = torch.tensor([t.next_state for t in batch], dtype=torch.float32, device=self.device)
        dones = torch.tensor([t.done for t in batch], dtype=torch.float32, device=self.device)

        q_values = self.net(states).gather(1, actions)

        with torch.no_grad():
            next_q_values = self.net(next_states).max(1).values
        expected_q_values = rewards + self.gamma * next_q_values * (1.0 - dones)

        loss = nn.SmoothL1Loss()(q_values, expected_q_values.unsqueeze(1))

        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_value_(self.net.parameters(), 100)
        self.optimizer.step()