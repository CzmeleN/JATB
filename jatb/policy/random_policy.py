from random import random
from jatb.policy.Ipolicy import IPolicy 

class RandomPolicy(IPolicy):
    def __init__(self, output_size: int) -> None:
        self.output_size = output_size
    
    def predict(self, observations: list[float]) -> list[float]: 
        return [random() for _ in range(self.output_size)]
