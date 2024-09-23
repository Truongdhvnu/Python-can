from CanTpCN import *
from typing import Dict
import threading
import can

canTpCnList = []

class CanTp:
    class CanTpReceiveHandle(can.Listener):
        def __init__(self, canTpConnectionMapping : Dict[int, CanTpCN], newConnectionCallback) -> None:
            self.newConnectionCallback = newConnectionCallback
            self.canTpConnectionMapping = canTpConnectionMapping
            # super().__init__()

        def on_message_received(self, msg) -> None:
            canTpConnection = self.canTpConnectionMapping[msg.arbitration_id]
            canTpConnection.recv_msgs_mutex.acquire()
            # print(f"Listener Receive: ID={hex(msg.arbitration_id)}, Data={msg.data}")      
            canTpConnection.revc_msgs_lst.append(msg)
            canTpConnection.recv_msgs_mutex.release()

            if isSingleFrame(msg) or isFirstFrame(msg):
                PduR_CanTpStartOfReception()
                self.newConnectionCallback(canTpConnection)
        pass

    def __init__(self, bus, canTpCnList:list[CanTpCN], canTpCnMapping : Dict[int, CanTpCN]) -> None:
        self.bus = bus
        self.canTpCnList = canTpCnList
        self.canTpCnMapping = canTpCnMapping
        self.notifier = can.Notifier(self.bus,[CanTp.CanTpReceiveHandle(self.canTpCnMapping, self.newConnectionHandle)])
        pass
    
    def newConnectionHandle(self, connection:CanTpCN):
        connection.receiveThreadHandle = threading.Thread(target=connection.AssembleMessage)
        connection.receiveThreadHandle.start()

    def canTp_Transmit(self, pduId:int, pduIdInfor: PduIdInfor):
        connection = self.canTpCnMapping[pduId]
        if (connection.transmitThreadHandle != None) and (connection.transmitThreadHandle.is_alive()):
            raise(RuntimeError(f"The canTp channel {connection.name} is occupied"))
        else:
            connection.transmitThreadHandle = threading.Thread(target= connection.TransmitMessage, args=(pduId, pduIdInfor))
            connection.transmitThreadHandle.start()
            # connection.transmitThreadHandle.join()

    def canTp_Stop(self):
        self.notifier.stop()
    # def waitUntilReceptionDone(self):
    #     if isinstance(self.receiveThreadHandle, threading.Thread):
    #         if self.receiveThreadHandle.is_alive():
    #             self.receiveThreadHandle.join()