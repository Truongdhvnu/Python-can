"""
    This file stimulate the right upper layer of canTP
    in Autosar architecture, it is the PduR
"""

class Std_ReturnType:
    E_NOT_OK = 0
    E_OK = 1

def PduR_CanTpStartOfReception():
    pass

def PduR_CanTpCopyRxData(pduId:int, pduInforType):
    pass

def PduR_CanTpRxIndication(pduId:int, result:Std_ReturnType):
    if result == Std_ReturnType.E_OK:
        print(f"+ Notified upper layer that the message with ID={hex(pduId)} is received sucessfuly")
    else:
        print(f"+ Notified upper layer that the message with ID={hex(pduId)} is not received sucessfuly")
    # Do the PduR layer logic
    pass

def PduR_CanTpTxConfirmation(pduId:int, result:Std_ReturnType):
    if result == Std_ReturnType.E_OK:
        print(f"+ Notified upper layer that the message with ID={hex(pduId)} is transmitted sucessfuly")
    else:
        print(f"+ Notified upper layer that the message with ID={hex(pduId)} is not transmitted sucessfuly")
    # Do the PduR layer logic
    pass


