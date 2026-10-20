from . import IInputHandler, IOutputHandler
from jatb.trackmania_interface.comm_manager import CommManager
from jatb.trackmania_interface.game_state import GameState

class Io:
    def __init__(self, 
                 input_handler: IInputHandler,
                 output_handler: IOutputHandler,
                 port: int,
                 addr: str, 
                 print_cd) -> None:
        
        self._input_handler = input_handler
        self._output_handler = output_handler
        self._comm_manager = CommManager(port, addr, print_cd)
        
    def launch(self) -> None:
        """ you need to invoke the function before using the class"""
        
        self._comm_manager.connect()
        
    def restart(self) -> None: 
        self._comm_manager.send_restart() 
        
    def send_output_to_the_game(self, policy_output: list[float]) -> None:
        self._output_handler.send_output_to_the_game(policy_output, self._comm_manager)
        
    def get_input(self, game_state: GameState) -> list[float]:
        return self._input_handler.get_input(game_state)
    
    def __del__(self) -> None:
        pass # TODO zaimplenetować zamykanie połączenia 