""" 
    Usage: poetry run python train_neat
        <name of file to save training result> 
        <liczba_epok>
        [port]
        [if you want to continue traing: name of file to load results from]
"""

import sys
from jatb.trainer import NeatTrainer
from jatb.scheduler import IScheduler # TODO potem sie zamieni na concrete scheduler

DEFAULT_PORT = 8450

def args_handler() -> tuple[str, int, int, bool, str]:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    save_path = sys.argv[1]
    epochs = int(sys.argv[2])
    port = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_PORT
    load_path = sys.argv[4] if len(sys.argv) > 4 else ""
    return save_path, epochs, port, bool(load_path), load_path

if __name__ == "__main__":
    save_path, epochs, port, continue_training, load_path = args_handler()
    
    scheduler: IScheduler = IScheduler() # TODO podmiana na concrete scheduler 
    trainer: NeatTrainer = NeatTrainer(scheduler, epochs, save_path, continue_training, load_path)
    trainer.train() 