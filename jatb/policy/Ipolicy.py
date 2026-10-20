from abc import ABC, abstractmethod

class IPolicy(ABC):
    @abstractmethod
    def __init__(self, output_size: int) -> None: ... 
    
    @abstractmethod 
    def predict(self, observations: list[float]) -> list[float]: ...