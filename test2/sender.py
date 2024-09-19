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
    
    bus = can.ThreadSafeBus(interface='neovi', channel=1, baudrate=500000, receive_own_messages=False) 

    sender_conection = CanTpCN(bus, "Test_Sender")

    msg = "hello"
    pduInforMapping[0x111] = [ord(c) for c in msg]

    msg2 = """The impact of foreign cultures is like a wave crashing onto the shore."""
    pduInforMapping[0x222] = [ord(c) for c in msg2]
    
    t1 = threading.Thread(target=CanTpCN.canTp_Transmit, args=(sender_conection, 0x222, pduInforMapping[0x222]))
    t1.start()

    while True:
        pass
