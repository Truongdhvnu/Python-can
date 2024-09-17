import time
import can
import threading

def task1():
    msg = can.Message(arbitration_id=0x021, data=[3, 4, 5, 1], is_extended_id=False)
    while 1:
        with can.ThreadSafeBus(interface='neovi', channel=1, bitrate=500000) as bus:
            bus.send(msg)
            print(f"S-Message: {msg.arbitration_id} : {msg.data}")

        time.sleep(5)

def task2():
    count = 0
    while 1:
        with can.ThreadSafeBus(interface='neovi', channel=1, bitrate=500000) as bus:
            msg2 = bus.recv(timeout=5)

        if msg2:
            print(f"Receive {count}: ID={hex(msg2.arbitration_id)}, Data={msg2.data}")
            # time.sleep(0.5)
            fc = can.Message(arbitration_id=0x020, data=[2], is_extended_id=False)
            bus.send(fc)
            
            count = count + 1
        else:
            print("Time out")

if __name__ == "__main__":
    thread2 = threading.Thread(target=task2)
    thread1 = threading.Thread(target=task1)

    thread2.start()
    thread1.start()

    thread1.join()
    thread2.join()