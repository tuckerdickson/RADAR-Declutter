import sys
import os
import socket

sys.path.append(os.getcwd() + '/utilities/output/')
import track_pb2

def dataframe_to_protomessage(input_df, output_path):
    def row_to_update_message(row, update):
        # Match each field in the dataframe row to its corresponding protomessage field
        df_proto_dict = {
            'UUID': 'uuid',
            'Name': 'name',
            'Create Time': 'create_time',
            'Update Time': 'update_time',
            'User Edit Time': 'user_edit_time',
            'Type': 'type',
            'Associated UUID': 'associated_uuid',
            'Note': 'note',
            'Source Name': 'source_name',
            'Source Class': 'source_class',
            'Source LID': 'source_lid',
            'Combat ID': 'combat_id',
            'Object ID': 'object_id',
            'Range To Contact': 'range_to_contact',
            'Bearing To Contact': 'bearing_to_contact',
            'Creator': 'creator',
            'Editor': 'editor',
            'AZ': 'az',
            'EL': 'el',
            'Range': 'range',
            'Position (lat)': 'position_lat',
            'Position (lon)': 'position_lon',
            'Position (alt MSL)': 'position_alt_msl',
            'Origin Position (lat)': 'origin_position_lat',
            'Origin Position (lon)': 'origin_position_lon',
            'Origin Position (alt MSL)': 'origin_position_alt_msl',
            '2525': '_2525',
            'Speed': 'speed',
            'Radar Cross Section': 'radar_cross_section',
            'Closest Time': 'closest_time',
            'Course': 'course',
            'Source ID': 'source_id',
            'Radial Velocity': 'radial_velocity',
            'Closest Distance': 'closest_distance',
            'Deleted': 'deleted',
            'Deleted Time': 'deleted_time',
            'AIS MMSI': 'ais_mmsi',
            'AIS IMO': 'ais_imo',
            'AIS Call Sign': 'ais_call_sign',
            'AIS Ship Type': 'ais_ship_type', 
            'AIS Destination': 'ais_destination',
            'AIS ETA': 'ais_eta',
            'Fused': 'fused',
            'Fused Tracks': 'fused_tracks',
            'Prediction': 'prediction',
            'Confidence': 'confidence'
        }

        for field, attr in df_proto_dict.items():
            # current method to see if column in dataframe row contains a value
            # if empty, returns false
            if row[field] == row[field]:
                setattr(update, attr, row[field])

    # create new buffer to hold all track updates for current time step
    tracks = track_pb2.Tracks()
    
    # for each row in the input dataframe, create a new message entry
    for _, row in input_df.iterrows():
        update = tracks.track.add()
        row_to_update_message(row, update)

    # Process for outputting protobuf messages to network
    # To demo, use output_receiver.py in seperate terminal to serve as host receiving messages
    # Currently only outputting to localhost at port 10002
    address = 'localhost'
    port = 10002
    
    # Serialize Message to String
    message = tracks.SerializeToString()
    
    # Create a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect to the receiving end
    server_address = (address, port)
    sock.connect(server_address)
    
    # Send the serialized message
    sock.sendall(message)
    
    # Clean up
    sock.close()