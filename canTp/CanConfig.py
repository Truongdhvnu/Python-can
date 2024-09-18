from typing import Dict

class PduIdConfig:
    def __init__(self, BS:int, ST_min:float) -> None:
        self.BS = BS
        self.ST_min = ST_min
        pass

"""
    This class is to simulate the PduIdInfor struct in autosar
    PduIdInfor (in autosar) contain the pointer to data of PDU and length of the data to transmit
    It is simply simulated by python list
"""
class PduIdInfor(list):
    pass

pduInforMapping : Dict[int, PduIdInfor] = {0x111:[], 0x222:[], 0x333:[]}

pduConfigMapping : Dict[int, PduIdConfig] = {0x111:PduIdConfig(3,0), 0x222:PduIdConfig(4,0), 0x333:PduIdConfig(5,0)}