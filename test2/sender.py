import can
import sys
sys.path.append('../')
from CanTpCN import *
from CanConfig import *

"""
    This test use "neovi" bus to test transmition of canTp using CanValue Device
    This code run in sender side
"""

if __name__ == "__main__":
    
    bus = can.ThreadSafeBus(interface='neovi', channel=1, baudrate=500000)

    sender_conection = CanTpCN(bus, "Test_Sender")

    msg = """hello"""
    pduInforMapping[0x111] = [ord(c) for c in msg]

    msg2 = """The impact of foreign cultures is like a wave crashing onto the shore. 
            When it recedes, it leaves behind pearls, seashells, or stones, all
            of which Chinese people collect eagerly at any cost."""
    pduInforMapping[0x222] = [ord(c) for c in msg2]

    # node1.canTp_Transmit(0x111, pduInforMapping[0x111])
    
    t1 = threading.Thread(target=CanTpCN.canTp_Transmit, args=(sender_conection, 0x111, pduInforMapping[0x111]))
    t1.start()

    count = 0
    while True:
        pass
