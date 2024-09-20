import can
import sys
sys.path.append('../')
from CanTpCN import *

"""
    This test use virtual bus to test transmition of canTp between two nodes
"""

if __name__ == "__main__":
    
    bus1 = can.ThreadSafeBus(interface='virtual', channel=1)
    bus2 = can.ThreadSafeBus(interface='virtual', channel=1)

    sender = CanTpCN(bus1, "Sender")
    receiver = CanTpCN(bus2, "Receiver")

    msg = "hello"
    pduInforMapping[0x111].SduDataPtr = [ord(c) for c in msg]

    msg2 = """The impact of foreign cultures is like a wave crashing onto the shore.
When it recedes, it leaves behind pearls, seashells, or stones, all
of which Chinese people collect eagerly at any cost.\n"""
    pduInforMapping[0x222].SduDataPtr = [ord(c) for c in msg2]

    
    t1 = threading.Thread(target=CanTpCN.TransmitMessage, args=(sender, 0x111, pduInforMapping[0x111]))
    t1.start()

    time.sleep(2)

    t2 = threading.Thread(target=CanTpCN.TransmitMessage, args=(sender, 0x222, pduInforMapping[0x222]))
    t2.start()

    count = 0
    while True:
        # node1.bus.send(can.Message(arbitration_id=id_lst[count], data=[3, 4, 5, 1], is_extended_id=False))
        # print(len(node2.revc_msgs_lst))
        # time.sleep(20)
        pass
