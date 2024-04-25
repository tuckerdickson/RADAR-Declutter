import socket
import os
import track_udp_pb2

BUFFER_LENGTH = 528

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the server address
server_address = ('localhost', 10002)
sock.bind(server_address)

print(f'Listening on {server_address}...')

while True:
    try:
        # Receive the protobuf message
        data, client_address = sock.recvfrom(BUFFER_LENGTH)

        # Deserialize the message
        received_message = track_udp_pb2.Tracks()
        received_message.ParseFromString(data)

        # Process the received message
        print(f'Received message from {client_address}:')
        print(received_message)
        print('\n')

    except KeyboardInterrupt:
        print("\nClosing Socket.")
        # Close the server socket
        sock.close()
        print("Stopping program.")
        break