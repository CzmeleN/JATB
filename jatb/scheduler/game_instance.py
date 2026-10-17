import os
import subprocess
import time

from jatb.trackmania_interface.comm_manager import CommManager

class GameInstance:
    def __init__(self, index: int, port: int, profile: str = "default") -> None:
        self.index = index
        self.port = port
        self.profile = profile
        self.comm: CommManager | None = None

    def launch(self) -> None:
        self.start_process()
        self.connect()

    def start_process(self) -> None:
        subprocess.Popen(
            ["wine", os.environ["TMLOADER"], "run", "TmForever", self.profile, f"/configstring=set jatb_port {self.port}"],
            cwd=os.environ["TMNF_GAME_DIR"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def connect(self) -> None:
        self.comm = CommManager(self.port)
        # TODO: connect() waits forever if the plugin never starts listening, add a timeout
        self.comm.connect()

    # one connection attempt that doesn't wait like connect(): False while the game is still loading
    def try_connect(self) -> bool:
        if self.comm is None:
            self.comm = CommManager(self.port)
        return self.comm.try_connect()

    # TODO: needs a reset message in jatb_link.as (Respawn / RewindToState), not a relaunch
    def reset(self) -> None:
        raise NotImplementedError

    def alive(self) -> bool:
        return subprocess.run(["pgrep", "-f", self.__process_pattern()], stdout=subprocess.DEVNULL).returncode == 0

    def port_in_use(self) -> bool:
        listening = subprocess.run(["ss", "-Hltn", f"sport = :{self.port}"], capture_output=True, text=True).stdout
        return bool(listening.strip())

    def close(self) -> None:
        if self.comm is not None and hasattr(self.comm, "sock"):
            self.comm.sock.close()
        self.comm = None

        # a game in a race can keep listening for a while after pkill (its socket is held by wineserver),
        # so wait until the port is free too, otherwise the next connection would reach the old game
        subprocess.run(["pkill", "-f", self.__process_pattern()])

        if self.__wait_closed(5):
            return

        # didn't exit on SIGTERM, kill it
        subprocess.run(["pkill", "-KILL", "-f", self.__process_pattern()])
        if not self.__wait_closed(5):
            raise RuntimeError(f"port {self.port} still in use after closing the game")

    def __wait_closed(self, timeout: float) -> bool:
        deadline = time.monotonic() + timeout
        while self.alive() or self.port_in_use():
            if time.monotonic() >= deadline:
                return False
            time.sleep(0.1)
        return True

    def __process_pattern(self) -> str:
        # match the exact port
        return rf"TmForever\.exe.*jatb_port {self.port}( |$)"
