import can
import time
import threading

bus1 = can.Bus(interface='virtual', channel=1)
bus1_revc_msgs_lst = []
bus1_send_msgs_lst = []
bus1_recv_msgs_mutex = threading.Lock()

bus2 = can.Bus(interface='virtual', channel=1)
bus2_revc_msgs_lst = []
bus2_send_msgs_lst = []
bus2_recv_msgs_mutex = threading.Lock()

class CanTpReceiveHandle(can.Listener):
    count = 0
    def on_message_received(self, msg: can.Message) -> None:
        bus1_recv_msgs_mutex.acquire()

        bus1_revc_msgs_lst.append(msg)
        print(f"Bus1 Receive {self.count}: ID={hex(msg.arbitration_id)}, Data={msg.data}") 

        bus1_recv_msgs_mutex.release()  
        return super().on_message_received(msg)
    
    def stop(self) -> None:
        count = 0
        return super().stop()

class CanTpReceiveHandle(can.Listener):
    count = 0
    def on_message_received(self, msg: can.Message) -> None:
        bus2_recv_msgs_mutex.acquire()

        print(f"Receive {self.count}: ID={hex(msg.arbitration_id)}, Data={msg.data}")      
        bus2_revc_msgs_lst.append(msg)

        bus2_recv_msgs_mutex.release()  
        return super().on_message_received(msg)
    
    def stop(self) -> None:
        count = 0
        return super().stop()

if __name__ == "__main__":
    
    id_lst = [0x19, 0x20, 0x21, 0x22, 0x23]

    can.Notifier(bus1, [CanTpReceiveHandle()])
    
    bus1.set_filters([{"can_id" : 0x21, "can_mask" : 0xFE, "extended" : False}])

    count = 0

    while True:
        bus2.send(can.Message(arbitration_id=id_lst[count], data=[3, 4, 5, 1], is_extended_id=False))
        count = (count + 1) % (len(id_lst) - 1)
        time.sleep(1)
        pass