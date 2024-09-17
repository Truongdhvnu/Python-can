import time
import can
import threading

bus1 = can.ThreadSafeBus(interface='virtual', channel=1)
bus2 = can.ThreadSafeBus(interface='virtual', channel=1)

def task1():
    msg = can.Message(arbitration_id=0x021, data=[3, 4, 5, 1], is_extended_id=False)
    while 1:
        bus1.send(msg)
        print(f"S-Message: ID={hex(msg.arbitration_id)}, Data={msg.data}")

        fc_recv = bus1.recv()
        if fc_recv:
            print(f"S-FC_recv: ID={hex(fc_recv.arbitration_id)}, Data={fc_recv.data}\n")
        else:
            pass
        time.sleep(2)

def task2():
    count = 0
    while 1:
        msg2 = bus2.recv()

        if msg2:
            print(f"Receive {count}: ID={hex(msg2.arbitration_id)}, Data={msg2.data}")
            # time.sleep(0.5)
            fc = can.Message(arbitration_id=0x020, data=[2], is_extended_id=False)
            bus2.send(fc)
            print(f"R-FlowCtrl {count}: ID={hex(fc.arbitration_id)}, Data={fc.data}")
            count = count + 1
        else:
            # print("Time out")
            pass

if __name__ == "__main__":
    thread2 = threading.Thread(target=task2)
    thread1 = threading.Thread(target=task1)

    thread2.start()
    thread1.start()

    thread1.join()
    thread2.join()