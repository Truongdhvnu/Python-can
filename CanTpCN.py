import can
import time
import threading
from CanTpFrame import *
from PduR import *
import random
import math

""" 
    Autosar
    [SWS_CanTp_00096] : The CanTp module shall support several connections simultaneously

    This class describe a connection channel of canTP layer 
    This class contain methods to handle transmit and receive message of a channel
"""
class CanTpCN:
    def __init__(self, bus:can.BusABC, name:str) -> None:
        self.bus = bus
        self.name = name
        self.revc_msgs_lst = []
        self.send_msgs_lst = []
        self.recv_msgs_mutex = threading.Lock()
        self.receiveThreadHandle = None
        self.transmitThreadHandle = None
        self.listener : can.Listener = None
        self.notifier : can.Notifier = None
        pass
    
    def getBufferMessage(self, timeout=0) -> CanTpFrame:
        start_time = time.time()

        msg = None
        while (msg == None):
            self.recv_msgs_mutex.acquire()
            # if len(self.revc_msgs_lst) > 1:
            #     raise(RuntimeError("Message size", len(self.revc_msgs_lst)))

            if len(self.revc_msgs_lst) > 0:
                msg = self.revc_msgs_lst[0]
                self.revc_msgs_lst.pop(0)
            self.recv_msgs_mutex.release() 

            if (time.time() - start_time > timeout):
                break
        return msg
    
    def handleWaitFlowControl(self, WFTmax:int) -> FlowStatus | None:
        fc_wait_count = 1

        while fc_wait_count <= WFTmax:
            fc_received = self.getBufferMessage(timeout=StaticConfig.N_Bs)
            assert isFlowControlFrame(fc_received)
            fc_received = FlowControl.deriveFromMessage(fc_received)
            
            if fc_received.FS == FlowStatus.CTS:
                print(f"{self.name} Transmiter side: Receive {fc_wait_count} FC.WAIT before receiving FC.CTS")
                return fc_received

            fc_wait_count += 1
        
        return None

    def TransmitMessage(self, pduId:int, pduIdInfor: PduIdInfor):
        msg_length = len(pduIdInfor.SduDataPtr)

        is_fd = False
        if pduConfigMapping[pduId].is_fd:
            SF_SDU_LENGTH = TX_DL - 2
            if msg_length < 4095:
                FF_SDU_LENGTH = TX_DL - 2 # FF_DL < 4095
            else:
                FF_SDU_LENGTH = TX_DL - 6 # FF_DL > 4095 (More 4 bytes are used to encode FF_DL)
            CF_SDU_LENGTH = TX_DL - 1
            is_fd = True
        else:
            SF_SDU_LENGTH = 7
            if msg_length < 4095:
                FF_SDU_LENGTH = 6       # FF_DL < 4095
            else:
                FF_SDU_LENGTH = 2       # FF_DL > 4095 (More 4 bytes are used to encode FF_DL)
            CF_SDU_LENGTH = 7

        pduIdInfor_subDataRequest = PduIdInfor()

        # If the transmit Frame is a Single Frame 
        if (msg_length <= SF_SDU_LENGTH):
            pduIdInfor_subDataRequest.SduDataPtr = 0
            pduIdInfor_subDataRequest.SduLength = msg_length
            """ Request data from upper layer """
            N_SDU = PduR_CanTpCopyRxData(pduId, pduIdInfor_subDataRequest)
            """ Send the SF """
            self.bus.send(SingleFrame(pduId=pduId, SF_DL=msg_length, N_SDU=N_SDU, is_fd=is_fd))
            return None
        
        # The message include First Frame and Consecutive Frame(s)
        pduIdInfor_subDataRequest.SduDataPtr = 0
        pduIdInfor_subDataRequest.SduLength = FF_SDU_LENGTH
        N_SDU = PduR_CanTpCopyRxData(pduId, pduIdInfor_subDataRequest)
        """ send the FF """

        ff = FirstFrame(pduId=pduId, FF_DL=msg_length, N_SDU=N_SDU, is_fd=is_fd) 
        self.bus.send(ff)
        print(f"{self.name}: transmit message FF_DL =", ff.FF_DL)
        
        """ Receive a Flow Controll before each block transmitting with time out is N_Bs """
        # These variables serve for coping segmentation data  
        start = FF_SDU_LENGTH - CF_SDU_LENGTH
        SN = 1

        while True:
            fc_received = self.getBufferMessage(timeout=StaticConfig.N_Bs)
            if fc_received == None:
                print(f"{self.name} Transmiter side: N_Bs timeout when waiting FC")
                PduR_CanTpTxConfirmation(pduId, Std_ReturnType.E_NOT_OK)
                return None
            else:
                """ Check if FC frame """
                assert isFlowControlFrame(fc_received)
                fc_received : FlowControl = FlowControl.deriveFromMessage(fc_received)

                print(f"{self.name}: receive FlowControl: FS={fc_received.FS}, BS={fc_received.BS}, ST_min={fc_received.ST_min}")

                if fc_received.FS == FlowStatus.OVFLW:
                    print("Receiver don't have enought available buffer. Exit Transmit")
                    PduR_CanTpTxConfirmation(pduId, Std_ReturnType.E_NOT_OK)
                    return None
                elif fc_received.FS == FlowStatus.WAIT:
                    fc_received = self.handleWaitFlowControl(WFTmax=pduConfigMapping[pduId].WFTmax)
                    if fc_received == None:
                        print("Receive exceed WTFmax time FC.WAIT")
                        PduR_CanTpTxConfirmation(pduId, Std_ReturnType.E_NOT_OK)
                        return None
    
                if fc_received.FS == FlowStatus.CTS:
                    # Receive blocksize number of Consecutive Frames
                    for _ in range(fc_received.BS):
                        time_stamp = time.time()
                        
                        # Upper layer's call for coping segmentation data
                        start += CF_SDU_LENGTH # Then start = FF_SDU_LENGTH at first time this statement called
                        length = CF_SDU_LENGTH if start + CF_SDU_LENGTH < msg_length else msg_length - start
                        pduIdInfor_subDataRequest.SduDataPtr = start
                        pduIdInfor_subDataRequest.SduLength = length
                        # print("start, end", start, end)
                        N_SDU = PduR_CanTpCopyRxData(pduId, pduIdInfor_subDataRequest)
                        
                        """
                            (ISO 15765-2)
                            N_Cs: Time until reception of the next consecutive frame N-PDU.
                            ST_min: The minimum time the sender is to wait between transmission of two CF N_PDUs.
                        """
                        ### time.time() can consume a lot of time
                        if time.time() - time_stamp > StaticConfig.N_Cs:
                            print("N_Cs timeout")
                            PduR_CanTpTxConfirmation(pduId, Std_ReturnType.E_NOT_OK)
                            return None
                        else:
                            continue_sleep = fc_received.ST_min - (time.time() - time_stamp)
                            if continue_sleep > 0:
                                time.sleep(continue_sleep)
                        time.sleep(fc_received.ST_min)

                        self.bus.send(ConFrame(pduId=pduId, SN=SN, N_SDU=N_SDU, is_fd=is_fd))
                        # print(f"{self.name} Transmiter side: Transmit CF data={''.join(chr(i) for i in N_SDU)}")
                        SN = (SN + 1) % 16

                        if (start + length == msg_length):
                            break
                    if (start + length == msg_length):
                        break
                    
        print(f"+ {self.name} transmited message sucessfully\n")
        PduR_CanTpTxConfirmation(pduId, Std_ReturnType.E_OK)

        pass

    def AssembleMessage(self):
        msg = self.getBufferMessage()
        id = msg.arbitration_id
        recv_mes = []
        FF_DL = 0

        # If the receive Frame is a Single Frame
        if isSingleFrame(msg):
            frame = SingleFrame.deriveFromMessage(msg=msg)
            if checkValidSF_DL(frame.SF_DL, len(msg.data)) == False:
                print("SF_DL is not match with data length received", frame.SF_DL, len(msg.data))
                PduR_CanTpRxIndication(id, Std_ReturnType.E_NOT_OK)
            else:
                print("Receive SF in thread:", frame.SF_DL, frame.N_SDU)
                PduR_CanTpRxIndication(id, Std_ReturnType.E_OK)
            return None
        
        # If the receive Frame is a First Frame
        assert isFirstFrame(msg)

        """
        (iso) The receiver retrieved value of RX_DL from the CAN_DL of the FF N_PDU
        """
        RX_DL = len(msg.data)
        msg = FirstFrame.deriveFromMessage(msg)
        FF_DL = msg.FF_DL
        recv_mes.extend(msg.N_SDU)
        print(f"{self.name}: Assembled incoming data: \"{''.join(chr(i) for i in msg.N_SDU)}\"")

        # print(f"Message's length: {recv_mes_length}, rec_msg start by: {''.join(chr(i) for i in recv_mes)}")

        BlockSize = pduConfigMapping[msg.arbitration_id].BS
        self.bus.send(FlowControl(pduId=msg.arbitration_id, FS=FlowStatus.CTS))
        
        desired_sequence_number = 1
        is_final_conFrame = False
        while True:
            transmision_done = False
            for _ in range(BlockSize):
                """
                    ISO 15765-2
                    N_Cr: Time until reception of the next consecutive frame N-PDU
                """
                msg = self.getBufferMessage(timeout=StaticConfig.N_Cr)

                if msg == None:
                    print(f"{self.name} Receive side: N_Cr timeout")
                    PduR_CanTpRxIndication(id, Std_ReturnType.E_NOT_OK)
                    return None

                msg = ConFrame.deriveFromMessage(msg)

                # length of CFs frame need to be match the RX_DL retrieved from FF, except final CF
                if FF_DL > len(recv_mes) + len(msg.N_SDU):
                    if len(msg.data) != RX_DL:
                        print("Length of CFs frame need to be match the RX_DL retrieved from FF, except final CF")
                        PduR_CanTpRxIndication(id, Std_ReturnType.E_NOT_OK)
                else:
                    is_final_conFrame = True

                # Check Sequence Number
                if desired_sequence_number != msg.SN:
                    print("Receive side: Sequence Number Error")
                    PduR_CanTpRxIndication(id, Std_ReturnType.E_NOT_OK)
                    return None
                else:
                    desired_sequence_number = (desired_sequence_number + 1) % 16

                if is_final_conFrame:
                    if (FF_DL - len(recv_mes) > 0):
                        print("Retrieved actual data from final CF with padded N_SDU")
                    final_segmented_data = msg.N_SDU[:FF_DL - len(recv_mes)]
                    recv_mes.extend(final_segmented_data)
                    print(f"{self.name}: Assembled final CF data: \"{''.join(chr(i) for i in final_segmented_data)}\"")
                else:
                    recv_mes.extend(msg.N_SDU)
                    print(f"{self.name}: Assembled imcomming frame's data: \"{''.join(chr(i) for i in msg.N_SDU)}\"")
                    
                # print(f"{self.name}: Current assembled message: {''.join(chr(i) for i in recv_mes)}, length: {len(recv_mes)}")
                
                if is_final_conFrame:
                    transmision_done = True
                    break
            
            if transmision_done:
                break
            
            ### Send wait if remaining bufer is not enough
            count = 0
            while self.isReceiveBufferAvaiable(BlockSize * RX_DL) == False:
                count += 1
                if count == pduConfigMapping[msg.arbitration_id].WFTmax:
                    print("Receive side: Reach WFTmax in a row. Abort connection")
                    PduR_CanTpRxIndication(id, Std_ReturnType.E_NOT_OK)
                    break
                self.bus.send(FlowControl(pduId=id, FS=FlowStatus.WAIT))
            ### Else sen CTS
            self.bus.send(FlowControl(pduId=id, FS=FlowStatus.CTS))

        print(f"+ {self.name} received message ID={hex(id)} succesfully from bus: \n{''.join(chr(i) for i in recv_mes)}")    
        PduR_CanTpRxIndication(id, Std_ReturnType.E_OK)

    def isReceiveBufferAvaiable(self, bufferSize):
        return random.choices([True, False], weights=[90, 10])[0]