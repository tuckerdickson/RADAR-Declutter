import struct
from CtcInMsg_Defs import *
from scapy.all import rdpcap


def decode_message(message):
    # comes from CtcInDataHeader in CtcInMsg_Defs.h (B <-> uint8_t, H <-> uint16_t, I <-> uint32_t)
    header_format = "=BBBBHIHH"

    # grab the header (first 14 bytes) from the message
    header_message = message[:struct.calcsize(header_format)]

    # unpack the raw header according to the format above, store in Python structure
    header_data = struct.unpack(header_format, header_message)
    header = CtcInDataHeader(header_data[0], header_data[1], header_data[2], header_data[3],
                             header_data[4], header_data[5], header_data[6], header_data[7])

    # grab the body (rest of the message after the header)
    body_message = message[struct.calcsize(header_format):]

    # there were 3 types of message in the network capture
    # type 1 is CtcInCommonMeasurement_3DPositionStruct (28-byte body, 42 bytes total)
    if header.msgType == 1:
        # body length should be 28 bytes
        assert len(body_message) == 28

        # comes from CtcInCommonMeasurement_3DPositionStruct in CtcInMsg_Defs.h
        # (h <-> int16_t, H <-> uint16_t, I <-> uint32_t)
        body_format = "=IIIhHHHHHHH"

        # unpack the raw body according to the format above, store in Python structure
        body_data = struct.unpack(body_format, body_message)
        body = CtcInCommonMeasurement_3DPositionStruct(header, body_data[0], body_data[1], body_data[2],
                                                       body_data[3], body_data[4], body_data[5], body_data[6],
                                                       body_data[7], body_data[8], body_data[9], body_data[10])

    # type 2 is CtcInCommonTrackDropStruct (4-byte body, 18 bytes total)
    elif header.msgType == 2:
        # body length should be 4 bytes
        assert len(body_message) == 4

        # comes from CtcInCommonSensorStatusStruct in CtcInMsg_Defs.h (I <-> uint32_t)
        body_format = "=I"

        # unpack the raw body according to the format above, store in Python structure
        body_data = struct.unpack(body_format, body_message)
        body = CtcInCommonTrackDropStruct(header, body_data[0])

    # type 3 is CtcInCommonSensorStatusStruct (30-byte body, 44 bytes total)
    elif header.msgType == 3:
        # body length should be 30 bytes
        assert len(body_message) == 30

        # comes from CtcInCommonSensorStatusStruct in CtcInMsg_Defs.h (I <-> uint32_t)
        body_format = "=IIIBBIIiI"

        # unpack the raw body according to the format above, store in Python structure
        body_data = struct.unpack(body_format, body_message)
        body = CtcInCommonSensorStatusStruct(header, body_data[0], body_data[1], body_data[2], body_data[3],
                                             body_data[4], body_data[5], body_data[6], body_data[7], body_data[8])


def extract_messages_from_pcap(file):
    packets = rdpcap(file)

    for packet in packets:
        if packet.haslayer("Raw"):
            message = packet.getlayer("Raw").load
            decode_message(message)


if __name__ == "__main__":
    pcap_file = "Contact_Export_Network_Capture.pcap"
    extract_messages_from_pcap(pcap_file)
