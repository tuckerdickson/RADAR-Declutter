import argparse
import CtcInMsg_Defs
import math
import pandas as pd
import socket
import struct
import time

from scapy.all import rdpcap

# keys: time stamps for the demo (in seconds), values: number of objects to send in that time stamp
LINES_PER_TIME = {
    0: 1,
    1: 1,
    2: 1,
    3: 1,
    4: 1,
    5: 1,
    6: 1,
    7: 1,
    8: 1,
    9: 1,
    10: 4,
    11: 4,
    12: 4,
    13: 4,
    14: 4,
    15: 4,
    16: 4,
    17: 4,
    18: 4,
    19: 4,
    20: 64,
    21: 64,
    22: 64,
    23: 64,
    24: 64,
    25: 64,
    26: 64,
    27: 64,
    28: 64,
    29: 64,
    30: 64,
    31: 64,
    32: 64,
    33: 64,
    34: 64,
    35: 64,
    36: 64,
    37: 64,
    38: 64,
    39: 64,
    40: 64,
    41: 64,
    42: 64
}

# maps UUIDs to integer track numbers
TRACK_NUMBERS = {}


def encode_message(hdr, body_df):
    """
    Encodes a DataFrame into a byte array to be sent to the receiver.
    :param hdr: The message header (type CtcInMsg_Defs.CtcInMsgHeader).
    :param body_df: The message body (as a DataFrame).
    :return: The byte array to be sent to the receiver.
    """
    # comes from CtcInDataHeader in CtcInMsg_Defs.h (B <-> uint8_t, H <-> uint16_t, I <-> uint32_t)
    header_format = "=BBBBHIHH"

    # grab the header (first 14 bytes) from the message
    header_list = get_hdr_list(hdr)

    # unpack the raw header according to the format above, store in Python structure
    header_data = struct.pack(header_format, header_list[0], header_list[1],
                              header_list[2], header_list[3], header_list[4],
                              header_list[5], header_list[6], header_list[7])

    # comes from CtcInCommonMeasurement_3DPositionStruct in CtcInMsg_Defs.h
    # (h <-> int16_t, H <-> uint16_t, I <-> uint32_t)
    body_format = "=IIIhHHHHHHH"

    # grab the body (rest of the message after the header)
    body_list = pd_to_ctc_body(body_df)

    # unpack the raw body according to the format above, store in Python structure
    body_data = struct.pack(body_format, body_list[0], body_list[1], body_list[2],
                            body_list[3], body_list[4], body_list[5], body_list[6],
                            body_list[7], body_list[8], body_list[9], body_list[10])

    return header_data + body_data


def get_grouped_data(path):
    """
    Reads data from a CSV file and groups by UUID.
    :param path: The path to the CSV file.
    :return: The DataFrame grouped by UUID.
    """
    # read the CSV into a DataFrame
    df = pd.read_csv(path)

    # group the data on UUID field
    grouped_df = df.groupby("UUID")

    # Drop the first 6 DataFrames (all are birds, we drop so that a drone shows up sooner in the demo)
    groups_to_keep = list(grouped_df.groups.keys())[7:]
    filtered_df = pd.concat([grouped_df.get_group(key) for key in groups_to_keep]).groupby("UUID")

    return filtered_df


def get_hdr_list(header_obj):
    """
    Returns the attributes of a CtcInDataHeader object as a list.
    :param header_obj: The CtcInDataHeader object to get the attributes from.
    :return: A list of header_obj's attributes.
    """
    return [
        header_obj.srcID,
        header_obj.msgBlockSeries,
        header_obj.msgType,
        header_obj.srcType,
        header_obj.msgLength,
        header_obj.msgNumber,
        header_obj.measurementTime_LSW,
        header_obj.measurementTime_MSW
    ]


def get_rows(time_sec, grouped_df):
    """
    Returns the appropriate rows (one per object) from the grouped DataFrame for the given time step.
    :param time_sec: The time step (in seconds) to fetch rows for.
    :param grouped_df: The Grouped DataFrame to fetch the rows from.
    :return: The rows for the given time step.
    """
    # store the rows to return as a list
    rows = []

    # a list of the UUIDs in grouped_df; we need to use these to index grouped_df later on
    all_keys = list(grouped_df.groups.keys())

    # keep track of the Objects whose rows we return; we will need to pop these particular rows from
    # their DataFrames later on.
    remove_keys = []

    # iterate over the objects that we need to return for the current time step (according to LINES_PER_TIME)
    for idx in range(LINES_PER_TIME[time_sec]):
        # get the current object from grouped_df
        df = grouped_df.get_group(all_keys[idx])

        # get the first row from the current object
        rows.append(df.iloc[0])

        # record that we're returning a row from the current object
        remove_keys.append(df.iloc[0]["UUID"])

    # for each object that we're returning a row for, pop the first row from that object's DataFrame
    modified_df = grouped_df.apply(lambda x: remove_first_row(x) if x.name in remove_keys else x)

    # return the rows and the new DataFrame with the returned rows popped off
    return rows, modified_df.reset_index(drop=True).groupby("UUID")


def parse_args(argv):
    """
    Parses and returns the command line arguments passed at runtime.
    :param argv: The command line arguments to parse.
    :return: The parsed arguments (as a dictionary).
    """
    # define the argument parser
    parser = argparse.ArgumentParser(
        prog="Radar Transmitter",
        description="""Sends messages to the Radar Declutter program, simulating the real-life radar system."""
    )

    # network host argument
    parser.add_argument("-ho", "--host",
                        type=str,
                        help="network host"
                        )

    # network port argument
    parser.add_argument("-p", "--port",
                        type=int,
                        help="network port"
                        )

    # whether running demonstration
    parser.add_argument("-d", "--demo",
                        action="store_true",
                        help="set True when running demonstration"
                        )

    # parse the arguments
    args = parser.parse_args(argv)

    # both network host and port must be specified
    if not (args.host and args.port):
        parser.error("listen mode requires both host and port")

    return args


def pd_to_ctc_body(pd_body):
    """
    Converts a
    :param pd_body:
    :return:
    """
    # decompose the speed into northward, eastward, and upward velocity
    vel = pd_body["Speed"] / math.sqrt(3)

    # if this is the first message sent, assign it track number 46626
    if len(TRACK_NUMBERS) == 0:
        track_num = 46626
        TRACK_NUMBERS[pd_body["UUID"]] = track_num

    # if this UUID is already associated with a track number, use that track number
    elif pd_body["UUID"] in TRACK_NUMBERS:
        track_num = TRACK_NUMBERS[pd_body["UUID"]]

    # if this UUID isn't associated with a track number, associate it with a new one.
    else:
        track_num = max(TRACK_NUMBERS.values()) + 1
        TRACK_NUMBERS[pd_body["UUID"]] = track_num

    # craft the list of data, according to the transformations specified in CtcInMsg_Defs.h
    data = [
        track_num,
        int(pd_body['Range'] * 16),
        int((pd_body['AZ'] * (2 ** 32)) / 360),
        int((pd_body['EL'] * (2 ** 16)) / 180),
        int(vel * 16),
        int(vel * 16),
        int(vel * 16),
        1024,
        int(pd_body['Radar Cross Section'] * 1000),
        61440,
        int(pd_body['Label'])
    ]
    return data


def remove_first_row(df):
    """
    Removes the first row from a DataFrame.
    :param df: The DataFrame to remove the row from.
    :return: The input df with the first row removed.
    """
    return df.iloc[1:]


def main(argv=None):
    """
    Main function of transmitter.py; parses arguments, loads and transforms the data, and sends it to the receiver.
    :param argv: The command line arguments.
    :return: None
    """
    # parse the command line arguments
    args = parse_args(argv)

    # create a UDP socket to send messages
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # if running in demonstration mode
    if args.demo:
        print("Transmitting Demo data")

        # load the data (grouped on UUID)
        grouped_df = get_grouped_data("../../../data/processed/crane/bird_drone_60.csv")

        # define a header for the messages (msgType should be 1, nothing else matters)
        header = CtcInMsg_Defs.CtcInDataHeader(0, 0, 1, 0, 0, 0, 0, 0)

        # iterate over all the time points in LINES_PER_TIME
        for t in range(max(LINES_PER_TIME.keys())):
            # get the rows for this time point from the grouped DataFrame
            rows, grouped_df = get_rows(t, grouped_df)

            # iterate over the rows for the time point, encode each row as a byte array and send to the receiver
            for row in rows:
                print(f"Sending message with UUID: {row["UUID"]}")
                encoded_message = encode_message(header, row)
                sock.sendto(encoded_message, (args.host, args.port))

            # send a message indicating that all rows for this time point have been sent
            sock.sendto(b'A', (args.host, args.port))

            # sleep between transmissions to imitate the radar system
            time.sleep(1)

    # if not running in demonstration mode
    else:
        # extract the packets from the network capture
        pcap_file = "Contact_Export_Network_Capture.pcap"
        packets = rdpcap(pcap_file)

        # for each packet, send the raw layer to the receiver then pause briefly
        for packet in packets:
            if packet.haslayer("Raw"):
                message_ = packet.getlayer("Raw").load
                sock.sendto(message_, (args.host, args.port))
                time.sleep(1)


if __name__ == "__main__":
    exit(main())
