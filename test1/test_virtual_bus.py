import can
import sys
sys.path.append('../')
from CanTp import *

"""
    This test use virtual bus to test transmition of canTp between two nodes
    Test using 2 devices and CanValue, see test2
"""

if __name__ == "__main__":
    # Use a virtual bus for each Conection for comunication between them
    virtual_bus1 = can.ThreadSafeBus(interface='virtual', channel=1, receive_own_messages=False)
    virtual_bus2 = can.ThreadSafeBus(interface='virtual', channel=1, receive_own_messages=False)
    canTpCnList = [] 
    canTpCnList.append(CanTpCN(virtual_bus1, "Sender"))
    canTpCnList.append(CanTpCN(virtual_bus2, "Receiver"))
    canTpConnectionMapping : Dict[int, CanTpCN] = {0x111:canTpCnList[0], 0x222:canTpCnList[1], 0x444:canTpCnList[0]}
    canTp = CanTp(None, canTpCnList, canTpConnectionMapping, interface="virtual")

    """
        Each ID is statically config with parameters in module CanConfig:
            BS      :   BlockSize
            ST_min  :   Minimum wait time betwen two CFs
            is_fd   :   canFD 
            WFTmax  :   Maximum WAIT FC in a row
        Each test use differrnt ID with different config to verify
    """

    ### Test case 1: ID=0x111: Classical CAN, Message is splited to SF and CFs
    print("Test case 1: ")
    msg = "Hello, My name is Joh"
    pduInforMapping[0x111].SduDataPtr = [ord(c) for c in msg]
    canTp.canTp_Transmit(0x111, pduInforMapping[0x111])
    time.sleep(1)
    print("Test case 1 end\n--------------------------------------------------------\n")



    ### Tes case 2: ID=0x444: Can FD transmit SF (check padding for can_FD)
    print("Test case 2: ")
    msg = "Hello world"  # SF_DL = 11 -> padding 3 byte 0xCC to N_SDU
    pduInforMapping[0x444].SduDataPtr = [ord(c) for c in msg]
    canTp.canTp_Transmit(0x444, pduInforMapping[0x444])
    time.sleep(1)
    print("Test case 2 end\n--------------------------------------------------------\n")



    ### Test case 3: 0x222: BS=4, is_fd=True, transmition of FF and CF"""
    print("Test case 3: CAN_FD, Message is splited to FF and CFs")
    msg2 = """Owing to the great variety of crimes that can be punishable by prison, some people
argue that not all criminals are the same and it would therefore be more appropriate to give
certain criminals community service instead. I agree that in some cases, prison may not be the
best solution and community service would probably have more benefits. One justification given 
for prisons is to keep society safe by removing criminals from the outside world. So the first 
thing to consider is if someone who has broken the law is a danger to other people. In the case 
of violent crime, there is an argument to keep the perpetrator away from society. However, burglary
or possession of drugs, for example, does not involve violence against other people so the criminal
does not present a direct danger to anyone in the community. Keeping these types of criminals in 
prison is expensive for the taxpayer and does not appear to be an effective punishment as they 
often commit the same crime again when they come out of prison.

Personally, I also believe punishments should reform people so they do not reoffend. 
A further reason not to put these people in prison is that they may mix with more dangerous
and violent criminals, potentially committing a worse crime when they are released. 
By keeping them in the community, helping others, they not only learn new skills, but they
could also develop more empathy and care towards others. If this occurs, society can only benefit.
One justification given for prisons is to keep society safe by removing criminals from the 
outside world. So the first thing to consider is if someone who has broken the law is a danger 
to other people. In the case of violent crime, there is an argument to keep the perpetrator 
away from society. However, burglary or possession of drugs, for example, does not involve 
violence against other people so the criminal does not present a direct danger to anyone in
the community. Keeping these types of criminals in prison is expensive for the taxpayer 
and does not appear to be an effective punishment as they often commit the same crime again
when they come out of prison.
Personally, I also believe punishments should reform people so they do not reoffend. A further 
reason not to put these people in prison is that they may mix with more dangerous and violent 
criminals, potentially committing a worse crime when they are released. By keeping them in the 
community, helping others, they not only learn new skills, but they could also develop more 
empathy and care towards others. If this occurs, society can only benefit.

Critics of this more rehabilitative approach to crime believe that justice should be harsh 
in order to deter people from committing similar crimes and that community service could be 
less likely to have that effect. However, there is very little evidence to suggest that long 
prison sentences deter criminals.

In conclusion, putting criminals who are not a danger to society in prison is expensive and, 
in my opinion, ineffective, both as a deterrent and as a form of rehabilitation. Community 
service for non-violent crimes benefits both society and the offender. That said, it would 
be useful to have more data to work out whether community service or prison is more likely 
to stop someone reoffending. I strongly believe that decisions on how best to deal with criminals 
should be based on evidence of what actually works.

Critics of this more rehabilitative approach to crime believe that justice should be harsh 
in order to deter people from committing similar crimes and that community service could be 
less likely to have that effect. However, there is very little evidence to suggest that long 
prison sentences deter criminals.

In conclusion, putting criminals who are not a danger to society in prison is expensive and, 
in my opinion, ineffective, both as a deterrent and as a form of rehabilitation. Community 
service for non-violent crimes benefits both society and the offender. That said, it would 
be useful to have more data to work out whether community service or prison is more likely 
to stop someone reoffending. I strongly believe that decisions on how best to deal with criminals 
should be based on evidence of what actually works.
Critics of this more rehabilitative approach to crime believe that justice should be harsh 
in order to deter people from committing similar crimes and that community service could be 
less likely to have that effect. However, there is very little evidence to suggest that long 
prison sentences deter criminals.

In conclusion, putting criminals who are not a danger to society in prison is expensive and, 
in my opinion, ineffective, both as a deterrent and as a form of rehabilitation. Community 
service for non-violent crimes benefits both society and the offender. That said, it would 
be useful to have more data to work out whether community service or prison is more likely 
to stop someone reoffending. I strongly believe that decisions on how best to deal with criminals 
should be based on evidence of what actually works.End\n"""

    print("len", len(msg2))
    pduInforMapping[0x222].SduDataPtr = [ord(c) for c in msg2]
    canTp.canTp_Transmit(0x222, pduInforMapping[0x222])
    time.sleep(1)
    print("Test case 3 end\n--------------------------------------------------------")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        canTp.canTp_Stop()
        virtual_bus1.shutdown()
        virtual_bus2.shutdown()
        pass
