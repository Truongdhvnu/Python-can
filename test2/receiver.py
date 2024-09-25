import can
import sys
sys.path.append('../')
from CanTpCN import *
from CanConfig import *
from CanTp import *

"""
    This test use "neovi" bus to test transmition of canTp using CanValue Device
    This code run in receiver side. Support multiple receive conection
    Sending message via canTp.canTp_Transmit also possible inside this code (Send & receive Connection at the same time)
    But is this test. Just describe the sender
"""

if __name__ == "__main__":
    
    bus = can.ThreadSafeBus(interface='neovi', channel=1, baudrate=500000, receive_own_messages=False)

    # Because two connection use the same Physical bus, they both use `bus` variable
    receiver_conection = CanTpCN(bus, "Test_Recv1")
    receiver_conection2 = CanTpCN(bus, "Test_Recv2")
    canTpCnList = [receiver_conection, receiver_conection2] 

    canTpCnMapping : Dict[int, CanTpCN] = {0x222:canTpCnList[0], 0x111:canTpCnList[1]}

    canTp = CanTp(bus, canTpCnList, canTpCnMapping)

    ## Receive (splited) message from (Multiple) connection 
    try:
        while True:
            pass
    except KeyboardInterrupt:
        canTp.canTp_Stop()
        bus.shutdown()
        pass
