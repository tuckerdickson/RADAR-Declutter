import math
import socket
import struct
import pandas as pd

from . import CtcInMsg_Defs


def calculate_position(range_dist, azimuth, elevation, sensor_lat=0.0, sensor_lon=0.0, sensor_alt=0.0):
    # convert az and el from degrees to radians
    azimuth_radians = math.radians(azimuth)
    elevation_radians = math.radians(elevation)

    # calculate the horizontal range from sensor to target
    horizontal_distance = range_dist * math.cos(elevation_radians)

    # use the horizontal range to calculate the change in latitude and longitude
    lat_change = horizontal_distance * math.cos(azimuth_radians)
    lon_change = horizontal_distance * math.sin(azimuth_radians)

    # calculate the vertical range from sensor to target (i.e., the change in altitude)
    alt_change = range_dist * math.sin(elevation_radians)

    # calculate the lat, lon, and alt of the object, assuming 111.32 km per 1 degree of latitude/longitude
    # https://stackoverflow.com/questions/639695/how-to-convert-latitude-or-longitude-to-meters
    object_lat = sensor_lat + (lat_change / 111320.0)
    object_lon = sensor_lon + (lon_change / 111320.0)
    object_alt = sensor_alt + alt_change

    return object_lat, object_lon, object_alt


def calculate_speed(north, east, up):
    return math.sqrt((north * north) + (east * east) + (up * up))


def ctc_to_pd(body):
    # extract fields from body (which is a CtcInCommonMeasurement_3DPositionStruct object)
    uuid = body.trackNumber

    # to get the azimuth, elevation, range, and RCS use the inverse transformation that was used to encode them
    azimuth = (body.azimuth * 360) / (2 ** 32)
    elevation = (body.elevation * 180) / (2 ** 16)
    range_ = body.range / 16
    rcs = body.RCS / 16

    # calculate the latitude, longitude, and altitude (using (40, -90, 200) as the reference point)
    lat, lon, alt = calculate_position(range_, azimuth, elevation, 40.0, -90.0, 200.0)

    # use inverse transformations to get the three directional velocity components
    velocityNorth = body.velocityNorth / 16
    velocityEast = (body.velocityEast * 22.5) / (2 ** 16)
    velocityUp = (body.velocityUp * 22.5) / (2 ** 16)

    # calculate speed using magnitude formula
    speed = calculate_speed(velocityNorth, velocityEast, velocityUp)

    # stick all the calculated fields into a DataFrame and return it
    data = {
        'UUID': [uuid],
        'Speed': [speed],
        'AZ': [azimuth],
        'EL': [elevation],
        'Range': [range_],
        'Position (lat)': [lat],
        'Position (lon)': [lon],
        'Position (alt MSL)': [alt],
        'Radar Cross Section': [rcs]
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
    def __init__(self, model, host, port, demo=None):
        self.model = model  # the classifier
        self.host = host    # IP address to connect on
        self.port = port    # port to connect on
        self.demo = demo    # NetworkDemo object (if running the demo) or None (if not running demo)

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

                        # when using the demo, 1-byte messages signify the last message of a time point
                        if len(data) == 1:
                            # not really sure what would happen if a non-demo 1-byte message was received...
                            try:
                                self.demo.update_plot()
                            # ...so we catch any exceptions that may arise, print, and continue
                            except Exception as e:
                                print(e)

                        # if the message isn't 1-byte, we assume it's a valid radar message with a header and a body
                        else:
                            # decode the message into the header and body
                            (header, body) = decode_message(data)

                            # messages of type 1 (CtcInCommonMeasurement_3DPositionStruct) are what we're interested in
                            if header.msgType == 1:
                                # convert the CtcInCommonMeasurement_3DPositionStruct object to a DataFrame
                                data_pd = ctc_to_pd(body)

                                # if running the demo
                                if self.demo is not None:
                                    # add the gt class (held in track descriptor flag field) to the DataFrame
                                    data_pd["Class"] = body.trackDescriptorFlag
                                    self.demo.run_test(data_pd)

                                # if not running the demo (i.e., standard inferencing)
                                else:
                                    self.model.make_inference(data_pd)

    def begin_listening(self):
        self.receive_messages()
