import can
import sys
sys.path.append('../')
from CanTpCN import *
from CanConfig import *
from CanTp import *
"""
    This test use "neovi" bus to test transmition of canTp using CanValue Device
    This code run in sender side
"""

if __name__ == "__main__":

    bus = can.ThreadSafeBus(interface='neovi', channel=1, baudrate=500000, receive_own_messages=False) 
    sender_connection = CanTpCN(bus, "Sender_1")
    sender_connection2 = CanTpCN(bus, "Sender_2")

    msg = "hello world!"
    pduInforMapping[0x111].SduDataPtr = [ord(c) for c in msg]

    msg2 = """Essay writing is not everyone's cup of tea.
Most students find it difficult to begin writing. 
Essays can be made easier if students start thinking 
about the topic either through brainstorming or by
putting them down on a sheet of paper. After getting
the ideas, they need to know how to organise them to
form an essay. For this, they need to practise essays
on different topics. Here, we have compiled a list of 
Essays on various topics. End"""

    print("Transmit message length", len(msg2))

    pduInforMapping[0x222].SduDataPtr = [ord(c) for c in msg2]

    # sender_connection.canTp_Transmit(0x222, pduInforMapping[0x222])

    canTpCnList = [sender_connection, sender_connection2] 
    canTpCnMapping : Dict[int, CanTpCN] = {0x111:canTpCnList[0], 0x222:canTpCnList[1]}

    canTp = CanTp(bus, canTpCnList, canTpCnMapping)

    canTp.canTp_Transmit(0x222, pduInforMapping[0x222])
    canTp.canTp_Transmit(0x111, pduInforMapping[0x111])

    try:
        while True:
            pass
    except KeyboardInterrupt:
        canTp.canTp_Stop()
        bus.shutdown()
        pass
