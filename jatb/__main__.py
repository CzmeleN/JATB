from jatb.game import Game, StepResult
from jatb.game.reward_function import IRewardFunction, DummyRewardFunction
from jatb.io.input_handler import IInputHandler, InputHandler0
from jatb.io.output_handler import IOutputHandler, OutputHandler0
from jatb.policy import IPolicy, RandomPolicy

GAME_SETTINGS = (
    "set unfocused_fps_limit false",
    "set skip_map_load_screens true",
    "set disable_forced_camera true",
    "set autorewind false",
)

def main() -> None:
    reward_function: IRewardFunction = DummyRewardFunction()
    input_handler: IInputHandler = InputHandler0()
    output_handler: IOutputHandler = OutputHandler0()
    policy: IPolicy = RandomPolicy(output_handler.get_output_size())
    
    game: Game = Game(reward_function,
                      input_handler,
                      output_handler,
                      "White/A01-Race.Challenge.Gbx")
    
    game.launch()
    while not game.is_finished:
        print("next step")
        observations: list[float] = game.get_observations()
        policy_output: list[float] = policy.predict(observations)
        step_result: StepResult = game.make_step(policy_output)

if __name__ == "__main__":
    main()
