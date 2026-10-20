"""Very short manual test for the JATB link / CommManager

Usage: py test.py [port] [map - unsupported yet]

Commands:
    1 full gas
    2 full brake
    3 steer left
    4 steer right
    5 reset inputs
    r restart race
    q quit
"""

import sys
import threading
from comm_manager import CommManager, ANALOG_MAX

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8450
# TODO: Make the map selection work
# MAP = sys.argv[2] if len(sys.argv) > 2 else "A01-Race.Challenge.Gbx"

alive = True

def reader(comm: CommManager) -> None:
    """reads frames to not fill the socket"""
    global alive
    try:
        while True:
            comm.recv_frame()
    except (ConnectionError, OSError):
        alive = False

def main() -> None:
    comm = CommManager(PORT, print_cd=200)
    comm.connect()
    threading.Thread(target=reader, args=(comm,), daemon=True).start()
    # TODO: Make the map selection work
    # comm.send_sel_lvl(MAP)

    actions = {
        "1": lambda: comm.send_gas(ANALOG_MAX),
        "2": lambda: comm.send_gas(-ANALOG_MAX),
        "3": lambda: comm.send_steer(-ANALOG_MAX),
        "4": lambda: comm.send_steer(ANALOG_MAX),
        "5": lambda: (comm.send_gas(0), comm.send_steer(0)),
        "r": comm.send_restart,
    }

    while alive:
        try:
            cmd = input().strip()
        except EOFError:
            break
        if cmd == "q":
            break

        action = actions.get(cmd)
        if action:
            action()
        else:
            print("unknown command")

if __name__ == "__main__":
    main()

