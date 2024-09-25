import can
import sys
sys.path.append('../')
from CanTpCN import *
from CanConfig import *
from CanTp import *

"""
    This test use "neovi" bus to test transmition of canTp using CanValue Device
    This code run in Sender side. Support multiple Send conection
    Receive message also possible inside this code (Send & Receive Connection at the same time)
    But is this test. Just describe the Sender
"""

if __name__ == "__main__":

    bus = can.ThreadSafeBus(interface='neovi', channel=1, baudrate=500000, receive_own_messages=False) 
    sender_connection = CanTpCN(bus, "Sender_1")
    sender_connection2 = CanTpCN(bus, "Sender_2")
    sender_connection3 = CanTpCN(bus, "Sender_3")

    msg = "hello world!"

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
could also develop more empathy and care towards others. If this occurs, society can only benefit.\n"""

    msg3 = """Owing to the great variety of crimes that can be punishable by prison, some people
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

    pduInforMapping[0x111].SduDataPtr = [ord(c) for c in msg]
    pduInforMapping[0x222].SduDataPtr = [ord(c) for c in msg2]
    pduInforMapping[0x444].SduDataPtr = [ord(c) for c in msg3]

    # print("Transmit message length", len(msg2))

    canTpCnList = [sender_connection, sender_connection2, sender_connection3] 
    canTpCnMapping : Dict[int, CanTpCN] = {0x111:canTpCnList[0], 0x222:canTpCnList[1], 0x444:canTpCnList[2]}

    canTp = CanTp(bus, canTpCnList, canTpCnMapping)

    # Multiple transmittion simultaneously
    canTp.canTp_Transmit(0x222, pduInforMapping[0x222])
    canTp.canTp_Transmit(0x111, pduInforMapping[0x111])
    canTp.canTp_Transmit(0x444, pduInforMapping[0x444])

    try:
        while True:
            pass
    except KeyboardInterrupt:
        canTp.canTp_Stop()
        bus.shutdown()
        pass
