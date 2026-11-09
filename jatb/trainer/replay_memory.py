from jatb.scheduler import Transition
from collections import deque
import random

class ReplayMemory(object):

    def __init__(self, capacity):
        self.memory = deque([], maxlen=capacity)

    def push(self, *args):
        """Save a transition"""
        self.memory.append(Transition(*args))

    def extend(self, transitions):
        """Save many transitions, once maxlen is reached the oldest ones drop out (like in push)"""
        self.memory.extend(transitions)

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)