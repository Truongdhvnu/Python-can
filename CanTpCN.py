import can
import time
import threading
from CanTpFrame import *
from CanTpUpperLayer import *

""" 
    Autosar
    [SWS_CanTp_00096] : The CanTp module shall support several connections simultaneously

    This class describe a connection channel of canTP layer 
    This class contain methods to handle transmit and receive message of a channel
"""
class CanTpCN:
    class CanTpReceiveHandle(can.Listener):
        def __init__(self, name:str, mutex:threading.Lock, buffer: list, callback) -> None:
            self.name = name
            self.buffer = buffer
            self.mutex = mutex
            self.handleReceiveConection = callback

        def on_message_received(self, msg) -> None:
            self.mutex.acquire()
            # print(f"{self.name} Receive: ID={hex(msg.arbitration_id)}, Data={msg.data}")      
            self.buffer.append(msg)
            self.mutex.release()

            if (msg.data[0] & 0xF0) == 0x00 or (msg.data[0] & 0xF0) == 0x10:
                PduR_CanTpStartOfReception()
                self.handleReceiveConection()
        pass

    def __init__(self, bus:can.BusABC, name:str) -> None:
        self.bus = bus
        self.name = name
        self.revc_msgs_lst = []
        self.send_msgs_lst = []
        self.recv_msgs_mutex = threading.Lock()
        self.listener = CanTpCN.CanTpReceiveHandle(name, self.recv_msgs_mutex, self.revc_msgs_lst, self.messageReceiveHandle)
        can.Notifier(self.bus, [self.listener])
        pass

    def canTp_SplitMessage(self, pduId:int, msg: list) -> list[CanTpFrame]:
        N_frames : list[CanTpFrame] = []
        msg_length = len(msg)

        if pduConfigMapping[pduId].is_fd:
            SF_SDU_LENGTH = 7
            FF_SDU_LENGTH = 6
            CF_SDU_LENGTH = 7
        else:
            SF_SDU_LENGTH = 7
            FF_SDU_LENGTH = 6
            CF_SDU_LENGTH = 7
            
        if (msg_length <= SF_SDU_LENGTH):
            N_frames.append(SingleFrame(pduId=pduId, SF_DL=msg_length, N_SDU=msg))
        else:
            N_frames.append(FirstFrame(pduId=pduId, FF_DL=msg_length, N_SDU=msg[0:FF_SDU_LENGTH]))

            count = -1
            end = -1
            SN = 0
            while (end != msg_length):
                count += FF_SDU_LENGTH + 1  # Then count = FF_SDU_LENGTH
                end = count + CF_SDU_LENGTH if count + CF_SDU_LENGTH < msg_length else msg_length
                N_frames.append(ConFrame(pduId=pduId, SN=SN, N_SDU=msg[count:end]))
                SN = (SN + 1) % 16

        print(f"{self.name}: The message is splited to:")
        for ms in N_frames:
            print("ID =",hex(ms.arbitration_id), ms.type, ms.data)

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
                """ Check if FC frame """
                assert isFlowControlFrame(msg) 
                msg = FlowControl.deriveFromMessage(msg)

                print(f"{self.name}: receive FlowControl: FS={msg.FS}, BS={msg.BS}, ST_min={msg.ST_min}")
                if msg.FS == FlowStatus.OVFLW:
                    print("Receiver don't have enought available buffer. Exit Transmit")
                elif msg.FS == FlowStatus.CTS:
                    # Receive blocksize Consecutive Frame
                    for _ in range(msg.BS):
                        time_stamp = time.time()
                        # Upper layer's callback
                        PduR_CanTpCopyRxData(pduId, pduInforMapping[pduId])
                        """
                            (ISO 15765-2)
                            N_Cs: Time until reception of the next consecutive frame N-PDU.
                            ST_min: The minimum time the sender is to wait between transmission of two CF N_PDUs.
                        """
                        if time.time() - time_stamp > StaticConfig.N_Cs:
                            PduR_CanTpRxIndication(pduId, Std_ReturnType.E_NOT_OK)
                        else:
                            time.sleep(msg.ST_min - (time.time() - time_stamp))

                        self.bus.send(N_Frames[frame_num])

                        frame_num += 1
                        if (frame_num == len(N_Frames)):
                            break
                    if (frame_num == len(N_Frames)):
                        break
                    
        print(f"+ {self.name} transmited message sucessfully\n")
        PduR_CanTpTxConfirmation(pduId, Std_ReturnType.E_OK)

        pass
    
    def messageReceiveHandle(self):
        t = threading.Thread(target=self.canTp_AssembleMessage)
        t.start()

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
        id = msg.arbitration_id
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

        self.bus.send(FlowControl(pduId=msg.arbitration_id, FS=FlowStatus.CTS))
        BlockSize = pduConfigMapping[msg.arbitration_id].BS
        
        desired_sequence_number = 0
        while True:
            transmision_aborted = False
            transmision_done = False
            for _ in range(BlockSize):
                """
                    ISO 15765-2
                    N_Cr: Time until reception of the next consecutive frame N-PDU
                """
                msg = self.getBufferMessage(timeout=StaticConfig.N_Cr)
                msg = ConFrame.deriveFromMessage(msg)

                if msg == None:
                    print("Receive side: N_Cr timeout")
                    PduR_CanTpRxIndication(id, Std_ReturnType.E_NOT_OK)
                    transmision_aborted = True
                    break

                # Check Sequence Number
                if desired_sequence_number != msg.SN:
                    print("Receive side: Sequence Number Error")
                    PduR_CanTpRxIndication(id, Std_ReturnType.E_NOT_OK)
                    transmision_aborted = True
                    break
                else:
                    desired_sequence_number = (desired_sequence_number + 1) % 16

                recv_mes.extend(msg.N_SDU)
                print(f"{self.name}: Current asembled message: {''.join(chr(i) for i in recv_mes)}, length: {len(recv_mes)}")
                
                if recv_mes_length == len(recv_mes):
                    transmision_done = True
                    break
            print("\n")
            
            if transmision_done or transmision_aborted:
                break
            self.bus.send(FlowControl(pduId=id, FS=FlowStatus.CTS))
        
        print(f"+ {self.name} received message succesfully from bus: \n{''.join(chr(i) for i in recv_mes)}")    
        PduR_CanTpRxIndication(id, Std_ReturnType.E_OK)