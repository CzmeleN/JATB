from . import IInputHandler, IOutputHandler
from jatb.trackmania_interface import CommManager, GameState, MapDataProvider, RecvFrame

class Io:
    def __init__(self, 
                 input_handler: IInputHandler,
                 output_handler: IOutputHandler,
                 port: int,
                 addr: str, 
                 print_cd: int, 
                 map_name: str) -> None:
        
        self._input_handler = input_handler
        self._output_handler = output_handler
        self._comm_manager = CommManager(port, addr, print_cd)
        self._map_data_provider = MapDataProvider(map_name)
        
    def launch(self) -> None:
        """ you need to invoke the function before using the class"""
        
        self._comm_manager.connect()
        
    def restart(self) -> None: 
        self._comm_manager.send_restart() 
        
    def send_output_to_the_game(self, policy_output: list[float]) -> None:
        self._output_handler.send_output_to_the_game(policy_output, self._comm_manager)
        
    def get_input(self, game_state: GameState) -> list[float]:
        return self._input_handler.get_input(game_state)
    
    @staticmethod
    def __vec3_to_tuple(v) -> tuple[float, float, float]:
        return (v.x, v.y, v.z)
    
    def __update_inplace_game_state_based_on_input_handler(self, game_state: GameState) -> None:
        frame: RecvFrame = self._comm_manager.get_latest_frame()
        
        game_state.set_velocity(Io.__vec3_to_tuple(frame.velocity))
        game_state.set_current_local_speed(Io.__vec3_to_tuple(frame.current_local_speed))
        game_state.set_orientation_up(Io.__vec3_to_tuple(frame.rotation[1]))
        game_state.set_orientation_forward(Io.__vec3_to_tuple(frame.rotation[2]))
        game_state.set_angular_velocity(Io.__vec3_to_tuple(frame.angular_velocity))
        game_state.set_gear(frame.gear)
        game_state.set_turning_rate(frame.turning_rate)
        game_state.set_is_finished(bool(frame.race_finished))
    
    def __update_inplace_game_state_based_on_map_data_provider(self, game_state: GameState) -> None: 
        # for now we don't use any data from map_data_provider
        pass
    
    def get_game_state(self) -> GameState:
        game_state: GameState = GameState()
        self.__update_inplace_game_state_based_on_input_handler(game_state)
        self.__update_inplace_game_state_based_on_map_data_provider(game_state)
        return game_state
    
    def __del__(self) -> None:
        pass # TODO zaimplenetować zamykanie połączenia 