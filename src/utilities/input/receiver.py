import socket
import struct
from CtcInMsg_Defs import *


def receive_messages(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))

        s.listen()
        print(f"Listening on {host}:{port}")

        while True:
            conn, addr = s.accept()
            print(f"Connected by: {addr}")

            with conn:
                while True:
                    data = conn.recv(1024)

                    if not data:
                        break

                    print(f"Received {len(data)} bytes from {addr}")



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


if __name__ == "__main__":
    HOST = "localhost"
    PORT = 12345
    receive_messages(HOST, PORT)
