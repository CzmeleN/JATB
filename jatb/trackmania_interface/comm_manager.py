from contextlib import contextmanager
import socket
import time
import ctypes as C
import sys
import threading
import numpy as np
import csv
from jatb.utils import Vec3, vec3_to_tuple
from collections.abc import Callable
from enum import IntEnum

# from jatb_link.as
class RecvFrame(C.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("frame_id",            C.c_int32),
        ("race_time",           C.c_int32),
        ("race_finished",       C.c_int32),
        # ("game_state",          C.c_int32),
        ("position",            Vec3),
        ("velocity",            Vec3),
        ("current_local_speed", Vec3),
        ("rotation",            Vec3 * 3),
        ("angular_velocity",    Vec3),
        ("gear",                C.c_int32),
        ("turning_rate",        C.c_float),
    ]
assert C.sizeof(RecvFrame) == 104

# to jatb_link.as
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

CSV_HEADER = [
    "frame_id", "race_time", "race_finished",
    "pos_x", "pos_y", "pos_z",
    "vel_x", "vel_y", "vel_z",
    "local_x", "local_y", "local_z",
    *[f"rot_{a}{b}" for a in "xyz" for b in "xyz"],
    "angvel_x", "angvel_y", "angvel_z",
    "gear", "turning_rate",
]

def _frame_to_list(f: RecvFrame) -> list:
    return [
        f.frame_id, f.race_time, f.race_finished,
        *vec3_to_tuple(f.position), *vec3_to_tuple(f.velocity), *vec3_to_tuple(f.current_local_speed),
        *(c for r in f.rotation for c in vec3_to_tuple(r)),
        *vec3_to_tuple(f.angular_velocity),
        f.gear, f.turning_rate,
    ]

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
        self._log_lock = threading.Lock()
        self._log_file = None
        self._log_writer = None

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

    def recv_frame(self) -> RecvFrame:
        return RecvFrame.from_buffer_copy(self._recv_n(C.sizeof(RecvFrame)))

    def start_receiving(self) -> None:
        """ starts a background thread keeping only the newest frame, call after connect() """
        threading.Thread(target=self._receive_loop, daemon=True).start()

    def _receive_loop(self) -> None:
        try:
            while True:
                frame = self.recv_frame() # blocking, must stay outside the lock
                # print(f"frame got {frame.frame_id}")
                with self._log_lock:
                    if self._log_writer is not None:
                        self._log_writer.writerow(_frame_to_list(frame))
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
            if self._latest_frame is None:
                raise RuntimeError("no frame after wait_for")

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

    def start_logging(self, path: str) -> None:
        with self._log_lock:
            if self._log_writer is not None:
                raise RuntimeError("already logging")
            self._log_file = open(path, "w", newline="")
            self._log_writer = csv.writer(self._log_file)
            self._log_writer.writerow(CSV_HEADER)

    def stop_logging(self) -> None:
        with self._log_lock:
            if self._log_file is not None:
                self._log_file.close()
            self._log_file = None
            self._log_writer = None

    @contextmanager
    def logging_to(self, path: str):
        self.start_logging(path)
        try:
            yield
        finally:
            self.stop_logging()

