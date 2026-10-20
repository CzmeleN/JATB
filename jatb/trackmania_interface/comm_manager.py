import socket
import time
import ctypes as C
import sys
import numpy as np
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
    print_cd: int
    print_counter: int

    def __init__(self, port: int, addr: str, print_cd: int):
        self.port = port
        self.addr = addr
        self.print_cd = print_cd
        self.print_counter = 0

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

    # TODO: return a Python-native type for the Bot
    def recv_frame(self) -> None:
        frame = RecvFrame.from_buffer_copy(self._recv_n(C.sizeof(RecvFrame)))
        fwd, up = _get_orientations(frame)

        self.print_counter += 1
        if (self.print_counter == self.print_cd):
            self.print_counter = 0
            print(f"Time since race start: {frame.race_time} ms")
            print(f"Finished: {frame.race_finished}")
            print(f"Velocity; {frame.velocity}")
            print(f"Local speed: {frame.current_local_speed}")
            print(f"Rotation: {frame.rotation}")
            print(f"Angular vel: {frame.angular_velocity}")
            print(f"Gear: {frame.gear}")
            print(f"Turning rate: {frame.turning_rate}")
            print(f"Forward: {fwd}, Up: {up}\n")

    def send_gas(self, gas: int) -> None:
        self._send(MsgType.SET_GAS, bytes(AnalogPayload(-_clamp(gas)))) # analog gas is reversed

    def send_steer(self, steer: int) -> None:
        self._send(MsgType.SET_STEER, bytes(AnalogPayload(_clamp(steer))))

    def send_execute(self, command: str) -> None:
        self._send(MsgType.EXECUTE, command.encode("ascii"))

    def send_sel_lvl(self, map_path: str) -> None:
        self.send_execute(f'map "{map_path}"')

    def send_restart(self) -> None:
        self._send(MsgType.RESTART)

