from abc import ABC, abstractmethod

class IPolicy(ABC):
    @abstractmethod 
    def predict(self, observation: list[float]) -> list[float]: ...
    
    