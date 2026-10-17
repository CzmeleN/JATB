from comm_manager import CommManager

c = CommManager(8450)
c.connect()

while True:
    frame = c.recv_frame()
    print(f"Time since race start: {frame.raceTime} ms")
