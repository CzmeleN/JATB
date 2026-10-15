from jatb.bot.policy import IPolicy
from jatb.bot.input_handler.Iinput_handler import IInputHandler
from jatb.bot.output_handler.Ioutput_handler import IOutputHandler


class Bot:
    def __init__(self, policy: IPolicy, input_handler: IInputHandler, output_handler: IOutputHandler) -> None:
        self.policy = policy
        self.input_handler = input_handler
        self.output_handler = output_handler

    def run(self) -> None:
        pass #TODO
        