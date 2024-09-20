from typing import Dict

TX_DL = 20

class PduIdConfig:
    def __init__(self, BS:int, ST_min:float=100, is_fd:bool=False, WFTmax=2) -> None:
        self.BS = BS
        self.ST_min = ST_min
        self.is_fd = is_fd
        self.WFTmax = WFTmax
        pass

"""
    This class is to simulate the PduIdInfor struct in autosar
    PduIdInfor (in autosar) contain the pointer to data of PDU and length of the data to transmit
    It is simply simulated by python list
"""
class PduIdInfor:
    def __init__(self):
        self.SduLength = 0
        self.SduDataPtr = []
    pass

pduInforMapping : Dict[int, PduIdInfor] = {0x111:PduIdInfor(), 0x222:PduIdInfor(), 0x333:()}

pduConfigMapping : Dict[int, PduIdConfig] = {0x111:PduIdConfig(BS=3), 0x222:PduIdConfig(BS=4, ST_min=127, is_fd=False, WFTmax=3), 0x333:PduIdConfig(BS=5)}

class StaticConfig:
    N_Ar = 0.1
    N_As = 0.1
    N_Br = 0.1
    N_Bs = 1
    N_Cr = 0.5
    N_Cs = 0.2
    pass

# N_Cr_Timeout : Waiting for CF time out (Receiver side)
# class StaticConfig:
#     N_Ar = 0.1
#     N_As = 0.1
#     N_Br = 0.1
#     N_Bs = 0.2
#     N_Cr = 0.14
#     N_Cs = 0.1
#     pass

# N_Bs_Timeout : Waiting for FC time out (Receiver side)
# class StaticConfig:
#     N_Ar = 0.1
#     N_As = 0.1
#     N_Br = 0.1
#     N_Bs = 0.1
#     N_Cr = 0.2
#     N_Cs = 0.1
#     pass