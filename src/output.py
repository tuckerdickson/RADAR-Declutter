import sys
import os
import socket
sys.path.append(os.getcwd() + '/utilities/proto/')

import track_pb2

def dataframe_to_protomessage(input_df, output_path):
    def row_to_update_message(row, update):
        # Match each field in the dataframe row to its corresponding protomessage field
        update.uuid = row['UUID']
       	
        # update.name = row['Name']
        # update.create_time = row['Create Time']
        # update.update_time = row['Update Time']
        # update.user_edit_time = row['User Edit Time']
        # update.type = row['Type']
        # update.associated_uuid = row['Associated UUID']
        # update.note = row['Note']
        # update.source_name = row['Source Name']
        # update.source_class = row['Source Class']
        # update.source_lid = row['Source LID']
        # update.combat_id = row['Combat ID']
        # update.object_id = row['Object ID']
        
        update.range_to_contact = row['Range To Contact']
        update.bearing_to_contact = row['Bearing To Contact']
        
        # update.creator = row['Creator']
        # update.editor = row['Editor']
        
        update.az = row['AZ']
        update.el = row['EL']
        update.range = row['Range']
        update.position_lat = row['Position (lat)']
        update.position_lon = row['Position (lon)']
        update.position_alt_msl = row['Position (alt MSL)']
        
        # update.origin_position_lat = row['Origin Position (lat)']
        # update.origin_position_lon = row['Origin Position (lon)']
        # update.origin_position_alt_msl = row['Origin Position (alt MSL)']
        # update._2525 = row['2525']
        
        update.speed = row['Speed']
        update.radar_cross_section = row['Radar Cross Section']
        
        # update.closest_time = row['Closest Time']
        # update.course = row['Course']
        # update.source_id = row['Source ID']
        
        update.radial_velocity = row['Radial Velocity']
        update.closest_distance = row['Closest Distance']
    
        # update.deleted = row['Deleted']
        # update.deleted_time = row['Deleted Time']
    
        # update.ais_mmsi = row['AIS MMSI']
        # update.ais_imo = row['AIS IMO']
        # update.ais_call_sign = row['AIS Call Sign']
        # update.ais_ship_type = row['AIS Ship Type']
        # update.ais_destination = row['AIS Destination']
        # update.ais_eta = row['AIS ETA']
        
        # update.fused = row['Fused']
        # update.fused_tracks = row['Fused Tracks']
    
        update.prediction = row['Prediction']
        update.confidence = row['Confidence']

    # create new buffer to hold all track updates for current time step
    tracks = track_pb2.Tracks()
    
    # for each row in the input dataframe, create a new message entry
    for _, row in input_df.iterrows():
        update = tracks.track.add()
        row_to_update_message(row, update)
        
    # currently writing to an output file (not much different than just writing to a csv)
    # TODO write to network output
    # with open(output_path, "wb") as f:
    #     f.write(tracks.SerializeToString())

    # Process for outputting protobuf messages to network
    # Requires seperate program to serve as host receiving messages
    # Currently only outputting to localhost at port 10000
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