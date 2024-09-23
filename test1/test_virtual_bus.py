import can
import sys
sys.path.append('../')
from CanTp import *

"""
    This test use virtual bus to test transmition of canTp between two nodes
    Test using 2 devices and CanValue, see test2
"""

if __name__ == "__main__":
    
    virtual_bus = can.ThreadSafeBus(interface='virtual', channel=1, receive_own_messages=True)

    canTpCnList = [] 
    canTpCnList.append(CanTpCN(virtual_bus, "Sender"))
    canTpCnList.append(CanTpCN(virtual_bus, "Receiver"))
    canTpConnectionMapping : Dict[int, CanTpCN] = {0x111:canTpCnList[0], 0x222:canTpCnList[1], 0x333:canTpCnList[1]}

    canTp = CanTp(virtual_bus, canTpCnList, canTpConnectionMapping)

    """ Test case 1: 0x111: BS=3, is_fd=False"""
    print("Test case 1: Classical CAN, Message is splited to SF and CFs")
    msg = "Hello world! My name is Truong"
    pduInforMapping[0x111].SduDataPtr = [ord(c) for c in msg]
    canTp.canTp_Transmit(0x111, pduInforMapping[0x111])
    time.sleep(5)
    print("Test case 1 end\n--------------------------------------------------------")

#     """ Test case 2: 0x222: BS=4, is_fd=True, transmition of FF and CF"""
#     print("Test case 2: CAN_FD, Message is splited to SF and CFs")
#     msg2 = """The impact of foreign cultures is like a wave crashing onto the shore.
# When it recedes, it leaves behind pearls, seashells, or stones, all
# of which Chinese people collect eagerly at any cost.\n"""
#     pduInforMapping[0x222].SduDataPtr = [ord(c) for c in msg2]
#     sender.canTp_Transmit(0x222, pduInforMapping[0x222])
#     time.sleep(0.5)
#     receiver.waitUntilReceptionDone()
#     print("Test case 2 end\n--------------------------------------------------------")

#     """ Test case 3: 0x333: BS=5, is_fd=True, transmition of SF canFD"""
#     print("Test case 3: CAN_FD, Message is a SF")
#     msg3 = """SF CanFD Msg"""
#     pduInforMapping[0x333].SduDataPtr = [ord(c) for c in msg3]
#     sender.canTp_Transmit(0x333, pduInforMapping[0x333])
#     time.sleep(0.5)
#     receiver.waitUntilReceptionDone()
#     print("Test case 3 end\n--------------------------------------------------------")

    count = 0
    while True:
        # node1.bus.send(can.Message(arbitration_id=id_lst[count], data=[3, 4, 5, 1], is_extended_id=False))
        # print(len(node2.revc_msgs_lst))
        # time.sleep(20)
        pass
