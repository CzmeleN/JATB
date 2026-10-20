from jatb.io.output_handler.Ioutput_handler import IOutputHandler
from jatb.trackmania_interface.comm_manager import CommManager

class OutputHandler0(IOutputHandler):
    """ 
    output: 
        [0] gas
        [1] left 
        [2] right 
        [3] gas + left 
        [4] gas + right 
        [5] nothing (don't press any key)
    """
    
    def get_output_size(self) -> int:
        return 6
     
    def send_output_to_the_game(self, output: list[float], comm_manager: CommManager) -> None:
        value_idx_to_send = output.index(max(output))
        
        match value_idx_to_send:
            case 0:
                self.__send_gas(output[0], comm_manager)
            case 1:
                self.__send_left(output[1], comm_manager)
            case 2:
                self.__send_right(output[2], comm_manager)
            case 3:
                self.__send_gas(output[3], comm_manager)
                self.__send_left(output[3], comm_manager)
            case 4:
                self.__send_gas(output[4], comm_manager)
                self.__send_right(output[4], comm_manager)
            case 5:
                pass
            
    @staticmethod
    def __clamp(val: float) -> float: 
        if val > 1.0: return 1.0 
        elif val < 0.0: return 0.0
        else: return val
        
    @staticmethod
    def __scale_val_0_1_to(val: float, l: float, r: float) -> int:
        # val: [0, 1]!
        scaled_value = l + (r - l) * val
        return int(scaled_value + 0.5) if scaled_value >= 0 else int(scaled_value - 0.5)
            
    @staticmethod
    def __scale_steer_left(val: float) -> int:
        val = OutputHandler0.__clamp(val)
        return OutputHandler0.__scale_val_0_1_to(val, -65536, 0)
    
    @staticmethod
    def __scale_steer_right(val: float) -> int:
        val = OutputHandler0.__clamp(val)
        return OutputHandler0.__scale_val_0_1_to(val, 0, 65536)
    
    @staticmethod
    def __scale_gas(val: float) -> int:
        val = OutputHandler0.__clamp(val)
        return OutputHandler0.__scale_val_0_1_to(val, 0, 65536)
        
    @staticmethod
    def __send_gas(val: float, comm_manager: CommManager) -> None:
        val = OutputHandler0.__scale_gas(val)
        comm_manager.send_gas(val)
    
    @staticmethod
    def __send_left(val: float, comm_manager: CommManager) -> None:
        val = OutputHandler0.__scale_steer_left(val)
        comm_manager.send_steer(val)
    
    @staticmethod
    def __send_right(val: float, comm_manager: CommManager) -> None:
        val = OutputHandler0.__scale_steer_right(val)
        comm_manager.send_steer(val)