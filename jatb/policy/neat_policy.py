from . import Ipolicy 

class NeatPolicy(Ipolicy):
    def __init__(self, output_size: int) -> None:
        self.output_size = output_size
        
    def predict(self, observations: list[float]) -> list[float]:
        pass 