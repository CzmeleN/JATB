from dataclasses import dataclass
from jatb.game.reward_function.IReward_function import IRewardFunction
from jatb.trackmania_interface.game_state import GameState
from jatb.io import IOutputHandler, IInputHandler, Io

SIMULATION_ONE_STEP_TIME_MS: int = 50

@dataclass
class StepResult: 
    step_observation: list[float]
    reward: float
    is_finished: bool

class Game:
    def __init__(self,
                reward_function: IRewardFunction,
                input_handler: IInputHandler,
                output_handler: IOutputHandler,
                map_name: str,
                max_race_time_ms: int = 10_000,
                port: int = 8450,
                addr: str = "127.0.0.1", 
                print_cd: int = 50) -> None:
        
        self.reward_function = reward_function
        self.map_name = map_name
        self.max_race_time_ms = max_race_time_ms
        self.current_race_time_ms: int = 0
        self.prev_game_state: GameState = GameState()
        self.is_finished: bool = False
        self.io = Io(input_handler, output_handler, port, addr, print_cd)
        
    def get_observations(self) -> list[float]:
        return self.io.get_input(self.prev_game_state)
        
    def reset(self) -> None:
        self.io.restart()
        # self._prev_game_state = jakaś_klasa_do_łączenia_inputu_z_comm_manager_i_danych_o_trasie_z_gry.get_state()
        # TODO: wait for the new race (countdown, negative race_time), then for its start, not the latest frame:
        #       wait_for_frame(lambda f: f.race_time < 0), then wait_for_frame(lambda f: f.race_time >= 0)
        
    def make_step(self, policy_output: list[float]) -> StepResult:
        self.io.send_output_to_the_game(policy_output)
        
        # new_state: GameState = jakaś_klasa_do_łączenia_inputu_z_comm_manager_i_danych_o_trasie_z_gry.get_state()
        # TODO: wait until the game advances by one step, not just take the latest frame:
        #       wait_for_frame(lambda f: f.race_time >= prev_race_time + SIMULATION_ONE_STEP_TIME_MS)
        
        last_step_observation: list[float] = self.io.get_input(new_state)
        reward = self.reward_function.compute(self.prev_game_state, new_state)
        self.is_finished = new_state.is_finished() or self.current_race_time_ms > self.max_race_time_ms
        
        self.prev_game_state = new_state 
        self.current_race_time_ms += SIMULATION_ONE_STEP_TIME_MS
        
        return StepResult(last_step_observation, reward, self.is_finished)
         
    def launch(self) -> None:
        """ you need to invoke the function before using the class"""
        
        self.io.launch()
        # self._prev_game_state: GameState = jakaś_klasa_do_łączenia_inputu_z_comm_manager_i_danych_o_trasie_z_gry.get_state()