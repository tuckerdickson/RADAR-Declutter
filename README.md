# RADAR Declutter

Enhancing radar surveillance by effectively distinguishing UAVs from birds.

## Table of Contents

- [About](#about)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)

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
2. Navigate to the project directory: `cd RADAR-Declutter`
3. Install the required dependencies: `pip install -r requirements.txt`
4. Navigate to the source directory: `cd src`

## Usage

* Follow these instructions to run the project using a real radar as the transmitter:
    1. Begin the receiver by running `python main.py listen --host <IP> --port <port>`, replacing `<IP>` and `<port>` with the IP address and port number that you want the transmitting radar to send messages to, respectively.
    2. Connect the transmitting machine to the receiving machine via ethernet. Ensure that the transmitting machine is actively transmitting updates. If the transmitting and receiving IP addresses and port numbers match, the receiver should immediately begin printing output to the console. If no updates are printing out on the receiving machine, there is likely a mismatch in the IP addresses or port numbers.

* Follow these instructions to run the project demo:
    1. Begin the receiver by running `python main.py demo --host <IP> --port <port>`, replacing `<IP>` and `<port>` with an available IP address and port number of your choice (we typically use `0.0.0.0` and `50000`, respectively).
    2. Begin the transmitter by running `python transmitter.py --host <IP> --port <port> --demo`, replacing `<IP>` and `<port>` with the same IP address and port number that you used for the receiver.
    3. Shortly after starting the transmitter, the demo window should appear.

* Follow these instructions to train a new model:

* Follow these instructions to test an existing model:

* Follow these instructions to change which model is used for classification:
    1. Within `constants.py` (`RADAR-Declutter/src/utilities/constants.py`), change `MODEL_PATH` to the path of the new model. All models should be stored in `RADAR-Declutter/models`, so you will likely only need to change the filename and not the rest of the path.

