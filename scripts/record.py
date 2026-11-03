"""Minimal util to log one line

Usage: poetry run python record.py <output.csv> [port]

Start before hopping into a race or in a middle of it, stop with ctrl+c or by finishing the race
"""

import sys
from jatb.trackmania_interface import CommManager

OUT = sys.argv[1]
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8450

def main() -> None:
    comm = CommManager(PORT, "127.0.0.1", print_cd=0)
    comm.connect()
    comm.start_receiving()

    print("waiting for the start")

    comm.wait_for_frame(lambda f: f.race_time >= -10)

    with comm.logging_to(OUT):
        print(f"started recording to {OUT}")
        try:
            comm.wait_for_frame(lambda f: f.race_finished == 1)
        except KeyboardInterrupt:
            print("stopped manually")

    print("finished recording")

if __name__ == "__main__":
    main()
