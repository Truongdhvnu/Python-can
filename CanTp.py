from CanTpCN import *
from typing import Dict
import threading
import can

""" Listener Handler for CanValue bus"""
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

""" Listener Handler for Virtual bus"""
class CanTpVirtualBusReceiveHandle(can.Listener):
    def __init__(self, connection:str, mutex:threading.Lock, buffer: list, callback) -> None:
        self.connection = connection
        self.buffer = buffer
        self.mutex = mutex
        self.handleReceiveConection = callback

    def on_message_received(self, msg) -> None:
        self.mutex.acquire()
        # print(f"{self.connection.name} Receive: ID={hex(msg.arbitration_id)}, Data={msg.data}")      
        self.buffer.append(msg)
        self.mutex.release()

        if isSingleFrame(msg) or isFirstFrame(msg):
            PduR_CanTpStartOfReception()
            self.handleReceiveConection(self.connection)
    pass

class CanTp:
    def __init__(self, bus:can.BusABC, canTpCnList:list[CanTpCN], canTpCnMapping : Dict[int, CanTpCN], interface="neovi") -> None:
        self.bus = bus
        self.canTpCnList = canTpCnList
        self.canTpCnMapping = canTpCnMapping
        self.interface = interface

        if interface == "virtual":
            for canTpCn in canTpCnList:
                canTpCn.listener = CanTpVirtualBusReceiveHandle(canTpCn, canTpCn.recv_msgs_mutex, canTpCn.revc_msgs_lst, self.newConnectionHandle)
                canTpCn.notifier = can.Notifier(canTpCn.bus, [canTpCn.listener])
        else:
            self.notifier = can.Notifier(self.bus, [CanTpReceiveHandle(self.canTpCnMapping, self.newConnectionHandle)])
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

    def canTp_Stop(self):
        if self.interface == "virtual":
            for canTpCn in self.canTpCnList:
                canTpCn.notifier.stop()
        else:
            self.notifier.stop()

    def waitUntilReceptionDone(self):
        for connection in self.canTpCnList:
            if isinstance(connection.receiveThreadHandle, threading.Thread):
                if connection.receiveThreadHandle.is_alive():
                    connection.receiveThreadHandle.join()