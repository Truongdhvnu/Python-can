# CanTp Layer Simulation (Autosar & ISO 15765-2)

## Project Overview
This project simulates the CAN Transport Protocol (CanTp) layer in accordance with Autosar and ISO 15765-2 standards. It supports various CAN features, including SF, FF, CF, FC frames, Classical CAN, CAN FD, multiple connections, error and timeout handling.

### Features:
- **Multiple Connections:** 
Supports multiple connections, with each connection handled by a separate thread.
Multiple ID can be map to a same connection and only a ID can use the connection at a time.
- **Bus support**: Virtual bus or Using Hardware
- **Frame:** Includes CanTp SF (Single Frame), FF (First Frame), CF (Consecutive Frame), and FC (Flow Control).
- **Classical CAN, CAN FD & Addressing:** Classical CAN and CAN FD, Normal addressing, Padding for both TX_DL <= 8 and TX_DL > 8
- **Timeout Handling:** Timeout handling for reliable communication.
- **Error Handling:** Handles errors related to such as Sequence Numbers (SN), valid frame types.
- **Parameter Simulation:** Parameters such as ST_min, WFTmax, N_Bs, N_Cs, N_Cr
- **Upper Layer Interaction:** TxConfirmation and TxIndication to PduR, following Autosar specification

### Code Structure
**Class diagram overview:**

![codestrt](https://github.com/user-attachments/assets/ed6f717e-c356-45dc-b396-88349c5d8a95)


- **CanTpFrame**: Classes SingleFrame, FirstFrame, ConFrame, FlowControl are to merge N_SDU, N_PCI parameters to Frame (Sender Side) and to extract the infomation form a message received from bus (Receiver Side). Addition functions for checking valid frame or padding N_SDU.
-  **CanTpCN:** Autosar requires CanTp module shall support several connections simultaneously. This class describe a connection channel of canTp layer, contain methods to handle transmit and receive message of a connection channel.
-  **CanTp:** This class is to handle multiple connection. It receives message from a callback function of can.Listener instance, deliver message to a certain conection. It also handles connection, for example, if multiple N_SDU is mapped with a conection, it makesure that only a N_SDU can use the conection at a time.
- **PduIdInfor & PduIdConfig**: Each PduID have its own config and Sdu information. Statically configured in `CanConfig` 
## Enviroment
- **Python 3.11.2**
- `python-can` with NeoVI support: `[neovi]`
- `python_ics`

- **For hardware testing**
- `Driver for CanValue`
- `icsneo40.dll`. In https://python-ics.readthedocs.io/en/master/
### Test
- **Hadware testing:** Using CanValue for testing trasmition between multiple computer, `test2` folder for testing example  
- **Virtual:**: Using virtual interface for testing. Test case in `test1` folder, 
