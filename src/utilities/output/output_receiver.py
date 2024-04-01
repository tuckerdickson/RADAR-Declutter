import socket
import os
import track_pb2
import socket

BUFFER_LENGTH = 1948
# Create a TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the server address
server_address = ('localhost', 10002)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection from main.py
    print('Waiting for a connection...')
    try:
        connection, client_address = sock.accept()
    except KeyboardInterrupt:
            print("\nClosing Socket.")
            #Close the server socket
            sock.close()
        
            print("Stopping program.")
            break
    try:
        print(f'Connection from {client_address}')

        # Receive the protobuf message data
        data = connection.recv(BUFFER_LENGTH)
        if not data:
            break

        # Deserialize the message
        received_message = track_pb2.Tracks()
        received_message.ParseFromString(data)

        # Process the received message
        print(received_message)
        print('\n')
    finally:
        # Clean up the connection
        connection.close()