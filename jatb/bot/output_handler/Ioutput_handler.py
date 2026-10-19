from abc import ABC, abstractmethod
from jatb.trackmania_interface.comm_manager import CommManager

class IOutputHandler(ABC):
    @abstractmethod
    def get_output_size(self) -> int: ...

    @abstractmethod 
    def send_output_to_the_game(self, output: list[float], comm_manager: CommManager) -> None: ...