import time
import can
import threading

# bus2 = can.interface.Bus(bustype='neovi', channel=42, bitrate=500000)
# shared_counter = 0

bus = can.ThreadSafeBus(interface='neovi', channel=1, bitrate=500000)

def task1():
    msg = can.Message(arbitration_id=0x021, data=[3, 4, 5, 1, 4, 5, 6, 7, 9], is_extended_id=False, is_fd=False)
    while 1:
        bus.send(msg, timeout=1)

        print(f"S-Message: ID={msg.arbitration_id} : {msg.data}")

        time.sleep(5)

def task2():
    count = 0
    while 1:
        msg2 = bus.recv(timeout=5)

        if msg2:
            print(f"Receive {count}: ID={hex(msg2.arbitration_id)}, Data={msg2.data}")
            # time.sleep(0.5)
            count = count + 1
        else:
            print("Time out")


def init():
    thread2 = threading.Thread(target=task2)
    thread1 = threading.Thread(target=task1)

    thread2.start()
    thread1.start()

    thread1.join()
    thread2.join()

init()
print("Program finished!")