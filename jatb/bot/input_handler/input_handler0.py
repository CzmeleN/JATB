from jatb.bot.input_handler.Iinput_handler import IInputHandler
from jatb.trackmania_interface import GameState


class InputHandler0(IInputHandler):
    """
    input:
        * current_local_speed x, y, z (3 inputs)
        * orientation_up (3 inputs)
        * angular velocity x, y, z (3 inputs)
        * gear
        * turning rate
        * heading_track sin, cos (2 inputs)
        * centerline lateral distance
        * distance to next corner
        * distance between next corner and next next corner 
        * next corner direction
        * next next corner direction 
    """
    
    def get_input(self, game_state: GameState) -> list[float]: 
        input: list[float] = []
        
        input.extend(game_state.get_current_local_speed())
        input.extend(game_state.get_orientation_up())
        input.extend(game_state.get_angular_velocity())
        input.append(game_state.get_gear())
        input.append(game_state.get_turning_rate())
        input.extend(game_state.get_heading_track())
        input.append(game_state.get_centerline_lateral_distance())
        input.append(game_state.get_distance_to_next_corner())
        input.append(game_state.get_distance_between_next_corners())
        input.append(game_state.get_next_corner_direction())
        input.append(game_state.get_next_next_corner_direction())
        
        return input
        
    def get_input_size(self) -> int:
	    return 18
