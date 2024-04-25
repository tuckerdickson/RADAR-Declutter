import sys
import os
import socket

sys.path.append(os.getcwd() + '/utilities/output/')
import track_udp_pb2

def dataframe_to_protomessage(input_df, output_path):
    def row_to_update_message(row, update):
        # Match each field in the dataframe row to its corresponding protomessage field
        df_proto_dict = {
            'UUID': 'uuid',
            'Class': 'source_class',
            'AZ': 'az',
            'EL': 'el',
            'Range': 'range',
            'Position (lat)': 'position_lat',
            'Position (lon)': 'position_lon',
            'Position (alt MSL)': 'position_alt_msl',
            'Speed': 'speed',
            'Radar Cross Section': 'radar_cross_section',
            'Prediction': 'prediction',
            'Confidence': 'confidence',
        }

        for field, attr in df_proto_dict.items():
            # current method to see if column in dataframe row contains a value
            # if empty, returns false
            if row[field] == row[field]:
                setattr(update, attr, row[field])

    # create new buffer to hold all track updates for current time step
    tracks = track_udp_pb2.Tracks()
    
    # for each row in the input dataframe, create a new message entry
    for _, row in input_df.iterrows():
        update = tracks.track.add()
        row['UUID'] = int(row['UUID'])
        row_to_update_message(row, update)

    # Process for outputting protobuf messages to network
    # To demo, use output_receiver.py in seperate terminal to serve as host receiving messages
    # Currently only outputting to localhost at port 10002
    address = 'localhost'
    port = 10002
    
    # Serialize Message to String
    message = tracks.SerializeToString()
    
    # Create a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Connect to the receiving end
    server_address = (address, port)
        
    # Send the serialized message
    sock.sendto(message, server_address)
    
    # Clean up
    sock.close()