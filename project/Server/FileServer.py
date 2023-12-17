# Main server script to handle client connections and requests.
# Include functions like handlePut, handleGet, handleChange, handleHelp, and handleBye.

from socket import *
from ServerUtilities import *

# Connecting to client
server_ip = '127.0.0.1'  # listen on all interfaces
server_port = 12000  # server port is fixed

server_socket=socket(AF_INET, SOCK_STREAM)
server_socket.bind((server_ip, server_port))

# Server begins listening for incoming TCP requests.
server_socket.listen(1)
print('The server is ready to receive')

# Loop forevaa
while True:
    # server waits on accept() for incoming requests, new socket created on return
    connection_socket, addr = server_socket.accept()
    print(f"Connection established with {addr}")

    keep_alive = True
    while keep_alive:
        # process the client's request
        client_request = connection_socket.recv(1024).decode()
        if not client_request:
            break  # break the loop if no request is received

        print("Received from client:", client_request)
        # Parse and handle the request
        command, filenames = parse_request(client_request)
        keep_alive = handle_request((command, filenames), connection_socket)

    connection_socket.close()