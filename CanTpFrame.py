import can
from collections.abc import Iterable
from CanConfig import *
from CanConfig import *

class FlowStatus:
    CTS = 0
    WAIT = 1
    OVFLW = 2

def isSingleFrame(msg:can.Message):
    return (msg.data[0] & 0xF0) == 0x00

def isFirstFrame(msg:can.Message):
    return (msg.data[0] & 0xF0) == 0x10

def isConFrame(msg:can.Message):
    return (msg.data[0] & 0xF0) == 0x20

def isFlowControlFrame(msg:can.Message):
    return (msg.data[0] & 0xF0) == 0x30

class CanTpFrame(can.Message):
    def __init__(self, timestamp: float = 0, arbitration_id: int = 0, is_extended_id: bool = True, is_remote_frame: bool = False, is_error_frame: bool = False, channel: int | str | None = None, dlc: int | None = None, data: bytes | bytearray | int | Iterable[int] | None = None, is_fd: bool = False, is_rx: bool = True, bitrate_switch: bool = False, error_state_indicator: bool = False, check: bool = False):
        super().__init__(timestamp, arbitration_id, is_extended_id, is_remote_frame, is_error_frame, channel, dlc, data, is_fd, is_rx, bitrate_switch, error_state_indicator, check)
        self.type = None

""" This padding for Single Frame with CAN_DL > 8"""
def singleFramePaddingHandle(N_SDU:list):
    N_Sdu_len = len(N_SDU)

    if N_Sdu_len <= 7:
        pass
    elif N_Sdu_len >= 8 and N_Sdu_len <= 10:
        padding = [0xCC for _ in range(12 - 2 - N_Sdu_len)] ## Padding N_SDU in order to CAN-DL equal 12 bit (2bit N_PCI)
        N_SDU.extend(padding)
    elif N_Sdu_len <= 14:
        padding = [0xCC for _ in range(16 - 2 - N_Sdu_len)] ## Padding N_SDU in order to CAN-DL equal 14 bit (2bit N_PCI)
        N_SDU.extend(padding)
    elif N_Sdu_len <= 18:
        padding = [0xCC for _ in range(20 - 2 - N_Sdu_len)] ## Padding N_SDU in order to CAN-DL equal 20 bit (2bit N_PCI)
        N_SDU.extend(padding)
    elif N_Sdu_len <= 22:
        padding = [0xCC for _ in range(24 - 2 - N_Sdu_len)] ## Padding N_SDU in order to CAN-DL equal 24 bit (2bit N_PCI)
        N_SDU.extend(padding)
    elif N_Sdu_len <= 30:
        padding = [0xCC for _ in range(32 - 2 - N_Sdu_len)] ## Padding N_SDU in order to CAN-DL equal 32 bit (2bit N_PCI)
        N_SDU.extend(padding)
    elif N_Sdu_len <= 46:
        padding = [0xCC for _ in range(48 - 2 - N_Sdu_len)] ## Padding N_SDU in order to CAN-DL equal 48 bit (2bit N_PCI)
        N_SDU.extend(padding)
    elif N_Sdu_len <= 62:
        padding = [0xCC for _ in range(64 - 2 - N_Sdu_len)] ## Padding N_SDU in order to CAN-DL equal 64 bit (2bit N_PCI)
        N_SDU.extend(padding)
    else:
        raise(RuntimeError("N_SDU does not fit into SF"))

def checkValidSF_DL(SF_DL, CAN_DL):
    if SF_DL < 1:
        return False
    
    if SF_DL <= 7 and (CAN_DL == SF_DL + 1):
        return True
    
    if  (SF_DL >= 8 and SF_DL <= 10 and CAN_DL == 12) or \
        (SF_DL >= 11 and SF_DL <= 14 and CAN_DL == 16) or \
        (SF_DL >= 15 and SF_DL <= 18 and CAN_DL == 16) or \
        (SF_DL >= 19 and SF_DL <= 22 and CAN_DL == 16) or \
        (SF_DL >= 23 and SF_DL <= 30 and CAN_DL == 16) or \
        (SF_DL >= 31 and SF_DL <= 46 and CAN_DL == 16) or \
        (SF_DL >= 47 and SF_DL <= 62 and CAN_DL == 16):
            return True
    else:
        return False
        
"""
    This class is to be call in both sender and receiver side
    Sender side: This class is to create Single frame from infor such as id, SF_DL, N_SDU
    Receiver S=side: when receiving message from bus, the receiver use this class to extract related data and PCI parameter 
"""
class SingleFrame(CanTpFrame):
    # def __new__(cls, data: list):
    #     # intending to check if datalegth is supported
    #     return super().__new__(cls)
    
    def __init__(self, msg:can.Message = None, pduId:int = None, SF_DL:int = None, N_SDU:list = None, is_ex=False, is_fd=False) -> None:
        self.SF_DL = SF_DL
        self.N_SDU = N_SDU.copy()

        """ Receiver side: init SF from received message """
        if msg != None:
            super().__init__(arbitration_id=msg.arbitration_id, data=msg.data, is_extended_id=msg.is_extended_id, is_fd=msg.is_fd)
            self.type = "SingleFrame"
            return None

        """ Sender side: init SF from N_PCI and N_SDU """
        singleFramePaddingHandle(N_SDU)
        # (CAN_DL > 8) <=> (using can FD)
        if is_fd:
            byte0 = 0x00
            byte1 = SF_DL
            N_SDU.insert(0, byte0)
            N_SDU.insert(1, byte1)
        else: # CAN_DL <= 8        
            # byte0 = /0x0/SF_DL/
            byte0 = (SF_DL & 0x0F)
            N_SDU.insert(0, byte0)
            
        super().__init__(arbitration_id=pduId, data=N_SDU, is_extended_id=is_ex, is_fd=is_fd)
        self.type = "SingleFrame"
        pass

    """ Receiver side: init SF from received message """
    def deriveFromMessage(msg:can.Message):
        if len(msg.data) > 8 : # CAN_DL > 8
            SF_DL = msg.data[1]
            N_SDU = msg.data[2:(SF_DL + 2)]
        else:
            SF_DL = msg.data[0] & 0x0F
            N_SDU = msg.data[1:(SF_DL + 1)]
        return SingleFrame(SF_DL=SF_DL, N_SDU=N_SDU, msg=msg, is_fd=msg.is_fd)

"""
    This class is to be call in both sender and receiver side
    Sender side: This class is to create Single frame from infor such as id, FF_DL, N_SDU
    Receiver S=side: when receiving message from bus, the receiver use this class to extract related data and PCI parameters
"""
class FirstFrame(CanTpFrame):
    def __init__(self, msg:can.Message = None, pduId:int = None, FF_DL:int = None, N_SDU:list = None, is_ex=False, is_fd=False) -> None:
        self.N_SDU = N_SDU.copy()
        self.FF_DL = FF_DL

        """ Receiver side: init FF from received message """
        if msg != None:
            super().__init__(arbitration_id=msg.arbitration_id, data=msg.data, is_extended_id=msg.is_extended_id, is_fd=msg.is_fd)
            self.type = "FirstFrame"
            return None

        """ Sender side: init FF from N_PCI and N_SDU """
        if FF_DL <= 4095:
            byte0 = 0x10
            byte0 |= (FF_DL >> 8) & 0x0F
            byte1 = FF_DL & 0xFF

            N_SDU.insert(0, byte0)
            N_SDU.insert(1, byte1)
        else:                   # FF_DL > 4095, using 4 byte to encode FF_DL
            byte0 = 0x10
            byte1 = 0x00
            byte2 = (FF_DL >> 24) & 0xFF
            byte3 = (FF_DL >> 16) & 0xFF
            byte4 = (FF_DL >> 8) & 0xFF
            byte5 = FF_DL & 0xFF
            N_SDU.insert(0, byte0)
            N_SDU.insert(1, byte1)
            N_SDU.insert(2, byte2)
            N_SDU.insert(3, byte3)
            N_SDU.insert(4, byte4)
            N_SDU.insert(5, byte5)

        super().__init__(arbitration_id=pduId, data=N_SDU, is_extended_id=is_ex, is_fd=is_fd)
        self.type = "FirstFrame"
    pass

    """ Receiver side: init SF from received message """
    def deriveFromMessage(msg:can.Message):
        temp = ((msg.data[0] << 8) & 0x0F00) | (msg.data[1] & 0xFF)
        if temp != 0:
            FF_DL = temp
            N_SDU = msg.data[2:]
        else:
            FF_DL = (msg.data[2] << 24) | (msg.data[3] << 16) | (msg.data[4] << 8) | msg.data[5]
            N_SDU = msg.data[5:]

        return FirstFrame(FF_DL=FF_DL, N_SDU=N_SDU, msg=msg)

""" This padding for Final Consecutive Frame"""
def finalConFramePaddingHandle(N_SDU:list):
    N_Sdu_len = len(N_SDU)

    if N_Sdu_len <= 7:
        padding = [0xCC for _ in range(8 - 1 - N_Sdu_len)] ## Padding N_SDU in order to CAN-DL equal 8 bit (1 bit N_PCI)
        N_SDU.extend(padding)
    elif N_Sdu_len >= 8 and N_Sdu_len <= 11:
        padding = [0xCC for _ in range(12 - 1 - N_Sdu_len)] ## Padding N_SDU in order to CAN-DL equal 12 bit (1 bit N_PCI)
        N_SDU.extend(padding)
    elif N_Sdu_len <= 15:
        padding = [0xCC for _ in range(16 - 1 - N_Sdu_len)] ## Padding N_SDU in order to CAN-DL equal 14 bit (1bit N_PCI)
        N_SDU.extend(padding)
    elif N_Sdu_len <= 19:
        padding = [0xCC for _ in range(20 - 1 - N_Sdu_len)] ## Padding N_SDU in order to CAN-DL equal 20 bit (1 bit N_PCI)
        N_SDU.extend(padding)
    elif N_Sdu_len <= 23:
        padding = [0xCC for _ in range(24 - 1 - N_Sdu_len)] ## Padding N_SDU in order to CAN-DL equal 24 bit (1 bit N_PCI)
        N_SDU.extend(padding)
    elif N_Sdu_len <= 31:
        padding = [0xCC for _ in range(32 - 1 - N_Sdu_len)] ## Padding N_SDU in order to CAN-DL equal 32 bit (1 bit N_PCI)
        N_SDU.extend(padding)
    elif N_Sdu_len <= 47:
        padding = [0xCC for _ in range(48 - 1 - N_Sdu_len)] ## Padding N_SDU in order to CAN-DL equal 48 bit (1 bit N_PCI)
        N_SDU.extend(padding)
    elif N_Sdu_len <= 63:
        padding = [0xCC for _ in range(64 - 1 - N_Sdu_len)] ## Padding N_SDU in order to CAN-DL equal 64 bit (1 bit N_PCI)
        N_SDU.extend(padding)
    else:
        raise(RuntimeError("N_SDU dose not fit into CF"))

"""
    This class is to be call in both sender and receiver side
    Sender side: This class is to create Single frame from infor such as id, SN, N_SDU
    Receiver S=side: when receiving message from bus, the receiver use this class to extract related data and PCI parameters 
"""
class ConFrame(CanTpFrame):
    def __init__(self, msg:can.Message = None, pduId:int = None, SN = None, N_SDU: list = None, padding = True, is_ex=False, is_fd=False) -> None:
        self.SN = SN
        self.N_SDU = N_SDU.copy()

        """ Receiver side: init CF from received message """
        if msg != None:
            super().__init__(arbitration_id=msg.arbitration_id, data=msg.data, is_extended_id=msg.is_extended_id, is_fd=msg.is_fd)
            self.type = "ConFrame"
            return None
        
        """ Sender side: init Consecutive Frame by N_PCI and N_SDU """
        if padding:
            finalConFramePaddingHandle(N_SDU)

        byte0 = 0x20
        byte0 |= (SN & 0x0F)

        N_SDU.insert(0, byte0)
        super().__init__(arbitration_id=pduId, data=N_SDU, is_extended_id=is_ex, is_fd=is_fd)
        self.type = "ConFrame"
    pass

    """ Receiver side: init CF from received message """
    def deriveFromMessage(msg:can.Message):
        SN = msg.data[0] & 0x0F
        N_SDU = msg.data[1:]
        return ConFrame(SN=SN, N_SDU=N_SDU, msg=msg)
    
"""
    This class is to be call in both sender and receiver side
    Sender side: This class is to create Flow Control from infor such as id, FS, BS, ST_min
    Receiver S=side: when receiving message from bus, the receiver use this class to extract related data and PCI parameters 
"""
class FlowControl(CanTpFrame):
    def __init__(self,  msg:can.Message = None, pduId:int = None, FS = None, BS= 1, ST_min = 127, is_ex=False, is_fd=False) -> None:
        self.FS = FS
        
            
        """ Receiver side: init FC from received message """
        if msg != None:
            super().__init__(arbitration_id=msg.arbitration_id, data=msg.data, is_extended_id=msg.is_extended_id, is_fd=msg.is_fd)
            """ Convert ST_min indicate by HEX to second (ISO)"""
            if (ST_min <= 0x7F):
                self.ST_min = ST_min * 0.001
            elif ST_min <= 0xF9 and ST_min >= 0xF1:
                self.ST_min = (ST_min & 0x0F) * 0.0001
            else:
                """Reserved ST_min -> Error handling by assign maximun sleep time (ISO)"""
                self.ST_min = 0.127
            self.BS = BS
            self.type = "FlowControl"
            return None
        
        """ Receiver side: init FlowControl by N_PCI """
        self.data = []
        byte0 = 0x30
        byte0 |= (FS & 0x0F)

        pduConfig = pduConfigMapping[pduId]

        byte1 = pduConfig.BS & 0xFF
        byte2 = pduConfig.ST_min & 0xFF

        self.data.append(byte0)
        self.data.append(byte1)
        self.data.append(byte2)

        # 3 protocol N/A reduntdant byte
        for _ in range(5):
            self.data.append(0x00)

        super().__init__(arbitration_id=pduId, data=self.data, is_extended_id=is_ex, is_fd=is_fd)
        self.type = "FlowControl"
        pass

    """ Receiver side: init FC from received message """
    def deriveFromMessage(msg:can.Message):
        FS = (msg.data[0] & 0x0F)
        BS = msg.data[1]
        ST_min = msg.data[2]
        return FlowControl(msg=msg, FS=FS, BS=BS, ST_min=ST_min)
    pass
    

