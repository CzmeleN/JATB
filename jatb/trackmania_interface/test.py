from comm_manager import CommManager

c = CommManager(8450)
c.connect()

while True:
    c.recv_frame()
