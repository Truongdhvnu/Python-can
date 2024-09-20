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
    pduInforMapping[0x111].SduDataPtr = [ord(c) for c in msg]

    msg2 = """Essay writing is not everyone's cup of tea.
Most students find it difficult to begin writing. 
Essays can be made easier if students start thinking 
about the topic either through brainstorming or by
putting them down on a sheet of paper. After getting
the ideas, they need to know how to organise them to
form an essay. For this, they need to practise essays
on different topics. Here, we have compiled a list of 
Essays on various topics."""

    print("Transmit message length", len(msg2))

    pduInforMapping[0x222].SduDataPtr = [ord(c) for c in msg2]
    
    t1 = threading.Thread(target=CanTpCN.TransmitMessage, args=(sender_conection, 0x222, pduInforMapping[0x222]))
    t1.start()

    while True:
        pass
