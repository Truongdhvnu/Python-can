# CanTp Layer Simulation (Autosar & ISO 15765-2)

## Project Overview
This project simulates the CAN Transport Protocol (CanTp) layer in accordance with Autosar and ISO 15765-2 standards. It supports various CAN features, including SF, FF, CF, FC frames, Classical CAN, CAN FD, multiple connections, error and timeout handling.

-  N_PCI parameters:

![abc](https://github.com/user-attachments/assets/cffb9469-fdfc-49c2-9e98-ccc378e2e6fc)

- Tranmistion FLow and Timming

![abcd](https://github.com/user-attachments/assets/54378c6b-d6db-4ebd-bf98-2b1be7ca8868)

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
