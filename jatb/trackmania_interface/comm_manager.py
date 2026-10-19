import socket
import time
import ctypes as C
import sys

# maybe move into a seperate file when we have more types ?
class RecvFrame(C.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("raceTime", C.c_int32)
    ]

assert C.sizeof(RecvFrame) == 4

class CommManager:
    port: int
    addr: str
    sock: socket.socket

    def __init__(self, port: int, addr: str = "127.0.0.1"):
        self.port = port
        self.addr = addr

    def __recv_n(self, n: int) -> bytes:
        buff = bytearray()

        while len(buff) < n:
            chunk = self.sock.recv(n - len(buff))

            if not chunk:
                raise ConnectionError("TMNF closed the connection")

            buff += chunk

        return bytes(buff)

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
        Frame = RecvFrame.from_buffer_copy(self.__recv_n(C.sizeof(RecvFrame)))
        print(f"Time since race start: {Frame.raceTime} ms")
    
    #TODO 
    def send_accelerate(self, val: float) -> None:
        raise NotImplemented
    
    #TODO 
    def send_steer(self, val: float) -> None:
        raise NotImplemented
    
