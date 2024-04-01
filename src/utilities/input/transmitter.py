import time

from scapy.all import rdpcap
from receiver import *


def send_message(host, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(message)
        print(f"Sent {len(message)}")


# def extract_messages_from_pcap(file):
#     packets = rdpcap(file)
#
#     for packet in packets:
#         if packet.haslayer("Raw"):
#             message = packet.getlayer("Raw").load
#             decode_message(message)


if __name__ == "__main__":
    HOST = "localhost"
    PORT = 12345

    pcap_file = "Contact_Export_Network_Capture.pcap"
    packets = rdpcap(pcap_file)

    for packet in packets:
        if packet.haslayer("Raw"):
            message = packet.getlayer("Raw").load
            send_message(HOST, PORT, message)
            time.sleep(5)
