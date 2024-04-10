import time
import socket

from scapy.all import rdpcap


def send_message(host, port, message):
    # create a socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(message)
        print(f"Sent {len(message)}")


if __name__ == "__main__":
    HOST = "localhost"
    PORT = 12345

    # extract the packets from the network capture
    pcap_file = "Contact_Export_Network_Capture.pcap"
    packets = rdpcap(pcap_file)

    # for each packet, send the raw layer to the receiver then pause briefly
    for packet in packets:
        if packet.haslayer("Raw"):
            message_ = packet.getlayer("Raw").load
            send_message(HOST, PORT, message_)
            time.sleep(1)
