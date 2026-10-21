import socket
import time
import ctypes as C
import sys
import threading
import numpy as np
from collections.abc import Callable
from enum import IntEnum

# maybe move into a seperate file when we have more types ?
class Vec3(C.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [("x", C.c_float), ("y", C.c_float), ("z", C.c_float)]

# from link.as
class RecvFrame(C.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("race_time",           C.c_int32),
        ("race_finished",       C.c_int32),
        # ("game_state",          C.c_int32),
        ("velocity",            Vec3),
        ("current_local_speed", Vec3),
        ("rotation",            Vec3 * 3),
        ("angular_velocity",    Vec3),
        ("gear",                C.c_int32),
        ("turning_rate",        C.c_float),
    ]
assert C.sizeof(RecvFrame) == 88

# to link.as
class MsgType(IntEnum):
    SET_GAS   = 1 # int32 [-65536, 65536]  : 4B
    SET_STEER = 2 # int32 [-65536, 65536]  : 4B
    RESTART   = 3 #                        : 0B
    EXECUTE   = 4 # console command        : ?B

class MsgHeader(C.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("type",        C.c_uint8),
        ("payload_len", C.c_uint16),
    ]
assert C.sizeof(MsgHeader) == 3

class AnalogPayload(C.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("value", C.c_int32),
    ]
assert C.sizeof(AnalogPayload) == 4

ANALOG_MAX = 65536
PAYLOAD_MAX = 0xFFFF

GAME_SETTINGS = (
    "set unfocused_fps_limit false",
    "set skip_map_load_screens true",
    "set disable_forced_camera true",
    "set autorewind false",
)

# TODO: add a correct return type
def _get_orientations(f: RecvFrame):
    R = np.stack([np.array([r.x, r.y, r.z], dtype=np.float32) for r in f.rotation])
    forward, up = R[:, 2], R[:, 1]
    return forward, up

def _clamp(val: int) -> int:
    if val < -ANALOG_MAX: return -ANALOG_MAX
    if val > ANALOG_MAX: return ANALOG_MAX
    return val

class CommManager:
    port: int
    addr: str
    sock: socket.socket
    print_cd: int # TODO: unused, remove after #27
    _cond: threading.Condition
    _latest_frame: RecvFrame | None
    _recv_error: Exception | None

    def __init__(self, port: int, addr: str, print_cd: int):
        self.port = port
        self.addr = addr
        self.print_cd = print_cd
        self._cond = threading.Condition()
        self._latest_frame = None
        self._recv_error = None

    def _recv_n(self, n: int) -> bytes:
        buff = bytearray()

        while len(buff) < n:
            chunk = self.sock.recv(n - len(buff))

            if not chunk:
                raise ConnectionError("TMNF closed the connection")

            buff += chunk

        return bytes(buff)

    def _send(self, msg_type: MsgType, payload: bytes = b"") -> None:
        if len(payload) > PAYLOAD_MAX:
            raise ValueError(f"payload too long ({len(payload)}B > {PAYLOAD_MAX}B)")

        header = MsgHeader(type=msg_type, payload_len=len(payload))
        self.sock.sendall(bytes(header) + payload)

    def connect(self) -> None:
        while True:
            try:
                self.sock = socket.create_connection((self.addr, self.port), timeout=2)
                self.sock.settimeout(None)

                print(f"JATB instance connected to {self.addr}:{self.port}")

                return
            except OSError:
                print(f"waiting for TMNF on port {self.port}", file=sys.stderr)

                time.sleep(1)

    def setup(self) -> None:
        for cmd in GAME_SETTINGS:
            self.send_execute(cmd)

    def recv_frame(self) -> RecvFrame:
        return RecvFrame.from_buffer_copy(self._recv_n(C.sizeof(RecvFrame)))

    def start_receiving(self) -> None:
        """ starts a background thread keeping only the newest frame, call after connect() """
        threading.Thread(target=self._receive_loop, daemon=True).start()

    def _receive_loop(self) -> None:
        try:
            while True:
                frame = self.recv_frame() # blocking, must stay outside the lock
                with self._cond:
                    self._latest_frame = frame
                    self._cond.notify_all()
        except Exception as e:
            with self._cond:
                self._recv_error = e
                self._cond.notify_all()

    def wait_for_frame(self, predicate: Callable[[RecvFrame], bool], timeout: float | None = None) -> RecvFrame:
        """ blocks until the newest frame satisfies predicate, returns its copy """
        with self._cond:
            ok = self._cond.wait_for(
                lambda: self._recv_error is not None
                        or (self._latest_frame is not None and predicate(self._latest_frame)),
                timeout)

            if self._recv_error is not None:
                raise ConnectionError("receiving frames stopped") from self._recv_error
            if not ok:
                raise TimeoutError("no matching frame from TMNF")

            return RecvFrame.from_buffer_copy(self._latest_frame)

    def get_latest_frame(self, timeout: float | None = None) -> RecvFrame:
        """ copy of the newest frame, waits only for the very first one """
        return self.wait_for_frame(lambda _: True, timeout)

    def send_gas(self, gas: int) -> None:
        self._send(MsgType.SET_GAS, bytes(AnalogPayload(-_clamp(gas)))) # gas is reversed

    def send_steer(self, steer: int) -> None:
        self._send(MsgType.SET_STEER, bytes(AnalogPayload(_clamp(steer))))

    def send_execute(self, command: str) -> None:
        self._send(MsgType.EXECUTE, command.encode("ascii"))

    def send_select_lvl(self, map_path: str) -> None:
        self.send_execute(f'map "{map_path}"')

    def send_restart(self) -> None:
        self._send(MsgType.RESTART)

