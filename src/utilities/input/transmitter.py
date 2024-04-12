import argparse
import time
import socket

from scapy.all import rdpcap


def send_message(host, port, message):
    # create a socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(message)
        print(f"Sent {len(message)}")


def main(argv=None):

    # define the argument parser
    parser = argparse.ArgumentParser(
        prog="Radar Transmitter",
        description="""Sends messages to the Radar Declutter program, simulating the real-life radar system."""
    )

    # network host, only required for LISTEN model
    parser.add_argument("-ho", "--host",
                        type=str,
                        help="network host"
                        )

    # network port, only required for LISTEN model
    parser.add_argument("-p", "--port",
                        type=int,
                        help="network port"
                        )

    # parse the arguments
    args = parser.parse_args(argv)

    # both network host and port must be specified
    if not (args.host and args.port):
        parser.error("listen mode requires both host and port")

    # extract the packets from the network capture
    pcap_file = "Contact_Export_Network_Capture.pcap"
    packets = rdpcap(pcap_file)

    # for each packet, send the raw layer to the receiver then pause briefly
    for packet in packets:
        if packet.haslayer("Raw"):
            message_ = packet.getlayer("Raw").load
            send_message(args.host, args.port, message_)
            time.sleep(1)


if __name__ == "__main__":
    exit(main())
