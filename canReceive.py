import can
import time

count = 0
while True:
    with can.Bus(interface='neovi', channel=1, bitrate=500000) as bus:
        msg = bus.recv(timeout=1)
    if msg:
        print(f"Receive {count}: ID={hex(msg.arbitration_id)}, Data={msg.data}")
    else:
        # print("Receive time out")
        pass
