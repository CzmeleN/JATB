from abc import ABC, abstractmethod

#TODO we need to implement sending data to tminterface first 
class IOutputHandler(ABC):
    @abstractmethod
    def get_output_size(self) -> int: ...
