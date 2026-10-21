"""Manual test of stepping every 50 ms of game time with CommManager.wait_for_frame

Usage: py step_test.py [port] [map]

Drives with full gas for STEPS steps, prints the lag of every step, then restarts the race.
"""

import math
import sys
import time
from comm_manager import CommManager, ANALOG_MAX

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8450
# Relative to Documents/TmForever/Tracks/Challenges, see README
MAP = sys.argv[2] if len(sys.argv) > 2 else "White/A01-Race.Challenge.Gbx"
STEP_MS = 50
STEPS = 100

def main() -> None:
    comm = CommManager(PORT, "127.0.0.1", print_cd=10**9) # silence recv_frame debug prints
    comm.connect()
    comm.setup()
    comm.start_receiving()
    comm.send_select_lvl(MAP)

    # frames from a race that was already running may still come in, the loaded map starts with a countdown
    comm.wait_for_frame(lambda f: f.race_time < 0, timeout=60)
    frame = comm.wait_for_frame(lambda f: f.race_time >= 0, timeout=10) # countdown over, the car can move
    print(f"race started: race_time={frame.race_time} ms")

    comm.send_gas(ANALOG_MAX)
    lags = []
    t_prev = time.monotonic()

    for i in range(STEPS):
        target = frame.race_time + STEP_MS
        frame = comm.wait_for_frame(lambda f: f.race_time >= target, timeout=2)

        now = time.monotonic()
        lag = frame.race_time - target
        lags.append(lag)
        v = frame.velocity
        print(f"step {i:3d}  race_time={frame.race_time:6d}  lag={lag:3d} ms  "
              f"wall_dt={(now - t_prev) * 1000:5.1f} ms  speed={math.hypot(v.x, v.y, v.z) * 3.6:6.1f} km/h")
        t_prev = now

    late = sum(1 for lag in lags if lag > 0)
    print(f"\nsteps late: {late}/{STEPS}, max lag: {max(lags)} ms")

    comm.send_gas(0)
    comm.send_restart()
    frame = comm.wait_for_frame(lambda f: f.race_time < 0, timeout=10) # countdown of the new race
    print(f"restart detected: race_time -> {frame.race_time} ms")

if __name__ == "__main__":
    main()
