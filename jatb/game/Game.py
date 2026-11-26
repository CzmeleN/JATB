from dataclasses import dataclass
from jatb.game.reward_function.IReward_function import IRewardFunction
from jatb.trackmania_interface.game_state import GameState
from jatb.io import IOutputHandler, IInputHandler, Io
from pathlib import Path
import os, signal
import subprocess

# TODO read from the settings or stay with the lowest possible?
VIRTUAL_DESKTOP_SIZE: str = "640x480"
SIMULATION_ONE_STEP_TIME_MS: int = 50
TMLOADER_PATH: Path = Path("~/tmnf/TMLoader/TMLoader.exe").expanduser()

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
                 print_cd: int = 50,
                 autologin: int | str = 1,
                 show_dxvk_hud: bool = False,
                 start_cmds: list[str] = []) -> None:

        self.reward_function = reward_function
        self.map_name = map_name
        self.max_race_time_ms = max_race_time_ms
        self.current_race_time_ms: int = 0
        self.prev_game_state: GameState = GameState()
        self.is_finished: bool = False
        self.io = Io(input_handler, output_handler, port, addr, print_cd, map_name, start_cmds)
        self.autologin = autologin
        self.show_dxvk_hud = show_dxvk_hud
        self._tm_process = None
        self.port = port

    def get_observations(self) -> list[float]:
        return self.io.get_input(self.prev_game_state)

    def reset(self) -> None:
        self.io.restart()
        self.io.wait_for_start()
        self.current_race_time_ms = 0
        self.prev_game_state = GameState()
        self.is_finished = False

    def make_step(self, policy_output: list[float]) -> StepResult:
        self.io.send_output_to_the_game(policy_output)

        new_state: GameState = self.io.get_game_state(SIMULATION_ONE_STEP_TIME_MS)
        self.current_race_time_ms = self.io.get_race_time()
        last_step_observation: list[float] = self.io.get_input(new_state)
        reward = self.reward_function.compute(self.prev_game_state, new_state)
        self.is_finished = new_state.get_is_finished() or self.current_race_time_ms > self.max_race_time_ms
        print(f"finished: {self.is_finished}, curr: {self.current_race_time_ms} / {self.max_race_time_ms}")

        self.prev_game_state = new_state 
        self.current_race_time_ms += SIMULATION_ONE_STEP_TIME_MS

        return StepResult(last_step_observation, reward, self.is_finished)

    def __launch_trackmania(self) -> None:
        if self._tm_process is not None:
            raise RuntimeError("TMNF is already running for this instance")

        env = os.environ.copy()
        if self.show_dxvk_hud:
            env["DXVK_HUD"] = "version,fps"

        # Need to use the Wine's virtual desktop, as launching 4 instances on one made them
        # fight for focus and sometimes unable to process input on Hyprland
        # cmd = ["wine", str(TMLOADER_PATH), "run", "TmForever", "default",
        #        f"/configstring=set autologin {self.autologin}; set jatb_port {self.port}"]
        cmd = ["wine", "explorer", f"/desktop=jatb{self.port},{VIRTUAL_DESKTOP_SIZE}",
               str(TMLOADER_PATH), "run", "TmForever", "default",
               f"/configstring=set autologin {self.autologin}; set jatb_port {self.port}"]

        self._tm_process = subprocess.Popen(
            cmd,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

    def close(self) -> None:
        if self._tm_process is None:
            return
        try:
            os.killpg(self._tm_process.pid, signal.SIGTERM)
            self._tm_process.wait(timeout=10)
        except ProcessLookupError:
            pass
        except subprocess.TimeoutExpired:
            os.killpg(self._tm_process.pid, signal.SIGKILL)
        self._tm_process = None

    def launch(self) -> None:
        """ you need to invoke the function before using the class"""

        self.__launch_trackmania() 
        self.io.launch()

