import can
import sys
sys.path.append('../')
from CanTpCN import *
from CanConfig import *

"""
    This test use "neovi" bus to test transmition of canTp using CanValue Device
    This code run in receiver side
"""

if __name__ == "__main__":
    
    bus = can.ThreadSafeBus(interface='neovi', channel=1, baudrate=500000, receive_own_messages=False)

    receiver_conection = CanTpCN(bus, "Test_Recv")
    
    while True:
        pass
