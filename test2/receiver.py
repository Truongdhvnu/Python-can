import can
import sys
sys.path.append('../')
from CanTpCN import *
from CanConfig import *
from CanTp import *

"""
    This test use "neovi" bus to test transmition of canTp using CanValue Device
    This code run in receiver side
"""

if __name__ == "__main__":
    
    bus = can.ThreadSafeBus(interface='neovi', channel=1, baudrate=500000, receive_own_messages=False)

    receiver_conection = CanTpCN(bus, "Test_Recv1")
    receiver_conection2 = CanTpCN(bus, "Test_Recv2")

    canTpCnList = [receiver_conection, receiver_conection2] 
    canTpCnMapping : Dict[int, CanTpCN] = {0x222:canTpCnList[0], 0x111:canTpCnList[1]}

    canTp = CanTp(bus, canTpCnList, canTpCnMapping)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        canTp.canTp_Stop()
        bus.shutdown()
        pass
