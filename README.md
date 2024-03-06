
## A system to support the monitoring of milling blade
The system is designed to increase production efficiency by allowing the monitoring of the blade's condition without the need for its disassembly, thereby minimizing the time required for tool inspection under a microscope. The main premise of the device is the use of a macro mode lens, connected to a camera operated by a microcomputer. A key aspect of the system is the TCP/IP communication protocol, which enables fast file transfer between the microcomputer responsible for taking pictures and interacting with the CNC machine and the computer connected to it. The computer program's graphical interface displays the received pictures, allowing for the assessment of the current condition of the milling blade. The system's software was entirely written in Python.

## Getting Started

### Essential items

- Raspberry PI
- Pi HQ Camera
- RGB LED HAT
- CNC controller (write to me to receive a ready sch and brd diagram)

### How to get started

- Unpack the files from the server folder on the Raspberry PI and then turn it on
- Connect the CNC machine via controller to the Raspberry PI 
- Unpack the rest of the files from the repository and then run them on the host computer connected to RPI
  
## Authors

- [@RibbeGlob](https://www.github.com/RibbeGlob)


## Example of how the program works

### Logging in
To successfully establish a connection with the server running on the microcomputer, it is necessary to select an IP address that matches the one the server is listening on.

![obraz](https://github.com/RibbeGlob/EngineeringWork/assets/108761666/1dfa01af-f022-4252-a387-1f5084a0a71f)


### Main GUI
After successfully establishing a connection with the microcomputer, the user gains access to an interface that offers an integrated environment for managing all aspects of the photographed tool.

![obraz](https://github.com/RibbeGlob/EngineeringWork/assets/108761666/499f475f-8422-4d00-b4aa-c1a456e8fddc)

### Live preview
Dedicated graphical interface for real-time camera image preview, allows for precise adjustment of the exposure parameters of the photographed tool. Thanks to this, the user can react in real time to lighting conditions and image quality, which is crucial for obtaining high-quality photos of the tool.

![obraz](https://github.com/RibbeGlob/EngineeringWork/assets/108761666/e04b1c74-a17d-4c52-8291-a678b6abd36c)

### Photo of the tool
After sending the taken photos through network sockets, one can notice the degradation of the tool.

![obraz](https://github.com/RibbeGlob/EngineeringWork/assets/108761666/fe2738f9-5964-4024-90b2-08a499368a18)
