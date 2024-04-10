import socket
import struct
import pandas as pd

from . import CtcInMsg_Defs


def ctc_to_pd(header, body):
    uuid = body.trackNumber
    azimuth = (body.azimuth * 360) / (2 ** 32)
    elevation = (body.elevation * 180) / (2 ** 16)
    range_ = body.range / 16

    data = {
        'UUID': [uuid],
        'Speed': [0],
        'AZ': [azimuth],
        'EL': [elevation],
        'Range': [range_],
        'Position (lat)': [0],
        'Position (lon)': [0],
        'Position (alt MSL)': [0]
    }

    df = pd.DataFrame(data)
    return df


def decode_message(message):
    # comes from CtcInDataHeader in CtcInMsg_Defs.h (B <-> uint8_t, H <-> uint16_t, I <-> uint32_t)
    header_format = "=BBBBHIHH"

    # grab the header (first 14 bytes) from the message
    header_message = message[:struct.calcsize(header_format)]

    # unpack the raw header according to the format above, store in Python structure
    header_data = struct.unpack(header_format, header_message)
    header = CtcInMsg_Defs.CtcInDataHeader(header_data[0], header_data[1], header_data[2], header_data[3],
                                           header_data[4], header_data[5], header_data[6], header_data[7])

    # grab the body (rest of the message after the header)
    body_message = message[struct.calcsize(header_format):]
    body = None

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
        body = CtcInMsg_Defs.CtcInCommonMeasurement_3DPositionStruct(header, body_data[0], body_data[1],
                                                                     body_data[2], body_data[3], body_data[4],
                                                                     body_data[5], body_data[6], body_data[7],
                                                                     body_data[8], body_data[9], body_data[10])

    # type 2 is CtcInCommonTrackDropStruct (4-byte body, 18 bytes total)
    elif header.msgType == 2:
        # body length should be 4 bytes
        assert len(body_message) == 4

        # comes from CtcInCommonSensorStatusStruct in CtcInMsg_Defs.h (I <-> uint32_t)
        body_format = "=I"

        # unpack the raw body according to the format above, store in Python structure
        body_data = struct.unpack(body_format, body_message)
        body = CtcInMsg_Defs.CtcInCommonTrackDropStruct(header, body_data[0])

    # type 3 is CtcInCommonSensorStatusStruct (30-byte body, 44 bytes total)
    elif header.msgType == 3:
        pass

        # body length should be 30 bytes
        assert len(body_message) == 30

        # comes from CtcInCommonSensorStatusStruct in CtcInMsg_Defs.h (I <-> uint32_t)
        body_format = "=IIIBBIIiI"

        # unpack the raw body according to the format above, store in Python structure
        body_data = struct.unpack(body_format, body_message)
        body = CtcInMsg_Defs.CtcInCommonSensorStatusStruct(header, body_data[0], body_data[1], body_data[2],
                                                           body_data[3], body_data[4], body_data[5],
                                                           body_data[6], body_data[7], body_data[8])

    return header, body


class Receiver:
    def __init__(self, model, host, port):
        self.model = model
        self.host = host
        self.port = port

    def receive_messages(self):
        # create a socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # bind the socket to the address and port
            s.bind((self.host, self.port))

            # listen for incoming connections
            s.listen()
            print(f"Listening on {self.host}:{self.port}")

            # keep the receiver listening indefinitely
            while True:
                # accept an incoming connection
                conn, addr = s.accept()

                # the following context manager will the connection is closed properly
                with conn:
                    # read in the transmitted data
                    while True:
                        data = conn.recv(1024)

                        # break if transmitter closed connection
                        if not data:
                            break

                        print(f"Received {len(data)} bytes from {addr}")

                        # decode the message
                        (header, body) = decode_message(data)

                        if header.msgType == 1:
                            data_pd = ctc_to_pd(header, body)
                            self.model.make_inference(data_pd)

    def begin_listening(self):
        self.receive_messages()
