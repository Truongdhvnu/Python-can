"""
    This file stimulate the right upper layer of canTP
    in Autosar architecture, it is the PduR
"""
from CanConfig import *

class Std_ReturnType:
    E_NOT_OK = 0
    E_OK = 1

def PduR_CanTpStartOfReception():
    pass

def PduR_CanTpCopyRxData(pduId:int, pduInforType:PduIdInfor):
    segmentedData = pduInforMapping[pduId].SduDataPtr[pduInforType.SduDataPtr : (pduInforType.SduDataPtr + pduInforType.SduLength)]
    return segmentedData

def PduR_CanTpRxIndication(pduId:int, result:Std_ReturnType):
    if result == Std_ReturnType.E_OK:
        print(f"+ Notified upper layer that the message with ID={hex(pduId)} is received sucessfully")
    else:
        print(f"+ Notified upper layer that the message with ID={hex(pduId)} is NOT received sucessfully")
    # Do the PduR layer logic
    pass

def PduR_CanTpTxConfirmation(pduId:int, result:Std_ReturnType):
    if result == Std_ReturnType.E_OK:
        print(f"+ Notified upper layer that the message with ID={hex(pduId)} is transmitted sucessfully")
    else:
        print(f"+ Notified upper layer that the message with ID={hex(pduId)} is NOT transmitted sucessfully")
    # Do the PduR layer logic
    pass


