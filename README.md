# RADAR Declutter

Short description of project.

## Table of Contents

- [About](#about)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## About

With small unmanned aerial vehicles becoming increasingly capable and inexpensive every day, the ability to quickly identify these potentially dangerous aircraft is more important than ever. RADAR Declutter leverages a lightweight machine learning algorithm to analyze kinematic information collected by radar and predict whether an aerial object is man-made or biological. 

## Getting Started

To get started with RADAR Declutter, follow these instructions:

### Prerequisites

Before running RADAR Declutter, you need to have the following software installed:
- contourpy==1.2.0
- cycler==0.12.1
- fonttools==4.47.2
- geopy~=2.4.1
- google~=3.0.0
- joblib==1.3.2
- kiwisolver==1.4.5
- matplotlib==3.8.2
- numpy==1.26.3
- packaging==23.2
- pandas==2.1.4
- pillow==10.2.0
- pyparsing==3.1.1
- python-dateutil==2.8.2
- pytz==2023.3.post1
- scapy~=2.5.0
- schedule~=1.2.1
- scikit-learn==1.3.2
- scipy==1.11.4
- six==1.16.0
- threadpoolctl==3.2.0
- tqdm~=4.66.2
- tzdata==2023.4

### Installation

1. Clone this repository: `git clone https://github.com/tuckerdickson/RADAR-Declutter.git`
2. Navigate to the source directory: `cd RADAR-Declutter/src`
3. Begin the receiver:
    * __If transmitting from radar:__ run `python main.py listen --host <IP> --port <port>`, replacing `<IP>` and `<port>` with the IP address and port number that you want the transmitting radar to send messages to, respectively. 
    * __If running the demo:__ run `python main.py demo --host <IP> --port <port>`, replacing `<IP>` and `<port>` with an available IP address and port number of your choice (we typically use `0.0.0.0` and `50000`, respectively).
4. Begin the transmitter:
    * __If transmitting from radar:__ connect the transmitting machine to the receiving machine by ethernet. Ensure that the transmitting machine is actively transmitting updates. If the transmitting and receiving IP addresses and port numbers match, the receiver should immediately begin printing output to the console.
    * __If running the demo:__ run `python transmitter.py --host <IP> --port <port> --demo`, replacing `<IP>` and `<port>` with the same IP address and port number that you used for the receiver.

## Usage

Provide examples or explain how to use your project.

## Contributing

Guidelines for contributing to your project. Include information on how to submit bug reports, suggest enhancements, or contribute code.

## License

Specify the license under which your project is released.

## Acknowledgements

Give credit to anyone whose code, libraries, or resources you used in your project.

