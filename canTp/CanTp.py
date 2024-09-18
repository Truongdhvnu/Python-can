import can
import time
import threading
from CanTpFrame import *

class StaticConfig:
    N_Ar = 0.1
    N_As = 0.1
    N_Br = 0.1
    N_Bs = 1
    N_Cr = 0.5
    N_Cs = 0.2
    pass

class CanNode:
    class CanTpReceiveHandle(can.Listener):
        def __init__(self, name:str, mutex:threading.Lock, buffer: list, callback) -> None:
            self.name = name
            self.buffer = buffer
            self.mutex = mutex
            self.callback = callback

        def on_message_received(self, msg) -> None:
            self.mutex.acquire()
            # print(f"{self.name} Receive: ID={hex(msg.arbitration_id)}, Data={msg.data}")      
            self.buffer.append(msg)
            self.mutex.release()

            if (msg.data[0] & 0xF0) == 0x00 or (msg.data[0] & 0xF0) == 0x10:
                # print("Call back called!")
                self.callback()
        pass

    def __init__(self, name:str) -> None:
        self.name = name
        self.bus = can.ThreadSafeBus(interface='virtual', channel=1)
        self.revc_msgs_lst = []
        self.send_msgs_lst = []
        self.recv_msgs_mutex = threading.Lock()
        self.listener = CanNode.CanTpReceiveHandle(name, self.recv_msgs_mutex, self.revc_msgs_lst, self.call_back)
        can.Notifier(self.bus, [self.listener])
        pass

    def canTp_SplitMessage(self, pduId:int, msg: list) -> list[CanTpFrame]:
        N_frames : list[CanTpFrame] = []
        msg_length = len(msg)

        if (msg_length <= 7):
            N_frames.append(SingleFrame(pduId=pduId, SF_DL=msg_length, N_SDU=msg))
        else:
            N_frames.append(FirstFrame(pduId=pduId, FF_DL=msg_length, N_SDU=msg[0:6]))

            count = -1
            end = -1
            SN = 0
            while (end != msg_length):
                count += 7
                end = count + 7 if count + 7 < msg_length else msg_length
                N_frames.append(ConFrame(pduId=pduId, SN=SN, N_SDU=msg[count:end]))
                SN = (SN + 1) % 16

        # for ms in N_frames:
        #     print(ms.arbitration_id, ms.type, ms.data)

        return N_frames

    def canTp_Transmit(self, pduId:int, msg: PduIdInfor):
        N_Frames = self.canTp_SplitMessage(pduId, msg)
        
        # If the transmit Frame is a Single Frame 
        if len(N_Frames) == 1:
            """ Send the SF """
            self.bus.send(N_Frames[0])
            return None
        
        # If the message include First Frame and Consecutive Frame(s)
        """ send the FF """
        self.bus.send(N_Frames[0])
        """ Receive a Flow Controll before each block transmitting with time out is N_Bs """
        frame_num = 1
        while True:
            msg : CanTpFrame = self.getBufferMessage(timeout=StaticConfig.N_Bs)
            if msg == None:
                print("Transmiter: N_Bs timeout after send FF")
                break
            else:
                assert isFlowControlFrame(msg) # Check if FC frame
                
                if (msg.data[0] & 0x0F) == FlowStatus.OVFLW:
                    print("Receiver don't have enought available buffer. Exit Transmit")
                elif (msg.data[0] & 0x0F) == FlowStatus.CTS:
                    for _ in range (msg.data[1] & 0x0F):
                        """
                            (ISO 15765-2)
                            N_Cs: Time until reception of the next consecutive frame N-PDU.
                            ST_min: The minimum time the sender is to wait between transmission of two CF N_PDUs.
                        """
                        sleep_time = msg.data[2] if msg.data[2] > StaticConfig.N_Cs else StaticConfig.N_Cs
                        time.sleep(sleep_time)
                        self.bus.send(N_Frames[frame_num])
                        frame_num += 1
                        if (frame_num == len(N_Frames)):
                            break
                    if (frame_num == len(N_Frames)):
                        break
        pass
    
    def call_back(self):
        t1 = threading.Thread(target=self.canTp_AssembleMessage)
        t1.start()

    def getBufferMessage(self, timeout=0) -> CanTpFrame:
        start_time = time.time()

        msg = None
        while (msg == None):
            self.recv_msgs_mutex.acquire()
            if len(self.revc_msgs_lst) > 0:
                msg = self.revc_msgs_lst[0]
                self.revc_msgs_lst.pop(0)
            self.recv_msgs_mutex.release() 

            if (time.time() - start_time > timeout):
                break
        return msg
    
    def canTp_AssembleMessage(self):
        msg = self.getBufferMessage()
        recv_mes = []
        recv_mes_length = 0

        # If the receive Frame is a Single Frame
        if isSingleFrame(msg):
            frame = SingleFrame.deriveFromMessage(msg=msg)
            print("Receive SF in thread:", frame.SF_DL, frame.N_SDU)
            return None
        
        # If the receive Frame is a First Frame
        assert isFirstFrame(msg)

        msg = FirstFrame.deriveFromMessage(msg)
        recv_mes_length = msg.FF_DL
        recv_mes.extend(msg.N_SDU)

        # print(f"Message's length: {recv_mes_length}, rec_msg start by: {''.join(chr(i) for i in recv_mes)}")

        fc_bs = 3
        self.bus.send(FlowControl(pduId=msg.arbitration_id, FS=FlowStatus.CTS))

        while True:
            transmision_aborted = False
            transmision_done = False
            for _ in range(fc_bs):
                """
                    ISO 15765-2
                    Time until reception of the next consecutive frame N-PDU
                """
                msg = self.getBufferMessage(timeout=StaticConfig.N_Cr)
                msg = ConFrame.deriveFromMessage(msg)

                if msg == None:
                    print("Receive side: N_Cr timeout")
                    transmision_aborted = True
                    break

                recv_mes.extend(msg.N_SDU)
                # print("Current asembled message:", ''.join(chr(i) for i in recv_mes), ", length:", len(recv_mes))
                
                if recv_mes_length == len(recv_mes):
                    transmision_done = True
                    break
            
            if transmision_done or transmision_aborted:
                break

            self.bus.send(FlowControl(pduId=msg.arbitration_id, FS=FlowStatus.CTS))
        
        print(f"{self.name} receive from bus:", ''.join(chr(i) for i in recv_mes))    
        print("Thread done\n")

if __name__ == "__main__":
    
    id_lst = [0x19, 0x20, 0x21, 0x22, 0x23]

    node1 = CanNode("node1")
    node2 = CanNode("node2")
    # node2.bus.send(can.Message(arbitration_id=0x123, data=[3, 4, 5, 1]))

    msg = """hello"""
    pduInforMapping[0x111] = [ord(c) for c in msg]

    msg2 = """The impact of foreign cultures is like a wave crashing onto the shore. 
            When it recedes, it leaves behind pearls, seashells, or stones, all
            of which Chinese people collect eagerly at any cost."""
    pduInforMapping[0x222] = [ord(c) for c in msg2]

    # msg = "hihi"

    # node1.canTp_Transmit(0x111, pduInforMapping[0x111])
    
    t1 = threading.Thread(target=CanNode.canTp_Transmit, args=(node1, 0x111, pduInforMapping[0x111]))
    t1.start()

    time.sleep(2)

    t2 = threading.Thread(target=CanNode.canTp_Transmit, args=(node1, 0x222, pduInforMapping[0x222]))
    t2.start()

    count = 0
    while True:
        # node1.bus.send(can.Message(arbitration_id=id_lst[count], data=[3, 4, 5, 1], is_extended_id=False))
        # node1.bus.send(msgs[0])

        # print(len(node2.revc_msgs_lst))
        count = (count + 1) % len(id_lst)
        time.sleep(20)
        pass