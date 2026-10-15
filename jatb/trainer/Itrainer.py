from abc import ABC, abstractmethod
from jatb.scheduler import IScheduler

class ITrainer(ABC):
    def __init__(self, scheduler: IScheduler) -> None:
        self.scheduler = scheduler

    @abstractmethod
    def train(self) -> None: ...