# Launches one game, reads 5 s of race time and closes it. Start a race by hand when asked.
#   source utils/env.sh
#   poetry run python -m jatb.scheduler.tests.game_test

from jatb.scheduler import GameInstance

EPISODE_MS = 5000

def main() -> None:
    game = GameInstance(index=0, port=8450)

    # close the game even on Ctrl+C or an error, otherwise TmForever is left behind
    try:
        game.launch()
        # the game starts in the menu and the plugin only sends frames during a race
        print("start a race in the game (any map)")

        race_time = 0
        while race_time < EPISODE_MS:
            race_time = game.comm.recv_frame().raceTime
            print(f"Time since race start: {race_time} ms")
    finally:
        game.close()

if __name__ == "__main__":
    main()
