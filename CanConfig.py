from typing import Dict

class PduIdConfig:
    def __init__(self, BS:int, ST_min:float, is_fd:bool=False) -> None:
        self.BS = BS
        self.ST_min = ST_min
        self.is_fd = is_fd
        pass

"""
    This class is to simulate the PduIdInfor struct in autosar
    PduIdInfor (in autosar) contain the pointer to data of PDU and length of the data to transmit
    It is simply simulated by python list
"""
class PduIdInfor(list):
    pass

pduInforMapping : Dict[int, PduIdInfor] = {0x111:[], 0x222:[], 0x333:[]}

pduConfigMapping : Dict[int, PduIdConfig] = {0x111:PduIdConfig(3,0), 0x222:PduIdConfig(4,0,False), 0x333:PduIdConfig(5,0)}

class StaticConfig:
    N_Ar = 0.1
    N_As = 0.1
    N_Br = 0.1
    N_Bs = 1
    N_Cr = 0.5
    N_Cs = 0.2
    pass
