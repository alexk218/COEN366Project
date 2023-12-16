# Main client script to interact with the server.
# Functions for user input processing and server communication.

# include socket library to create/manage TCP & UDP connections
from socket import *
from ClientUtilities import *

# Enter server's IP address and port #.
server_ip = input("Enter the server IP address: ")
# Convert input from string to int. Socket library expects integer for port.
server_port = int(input("Enter the server port number: "))

# Create TCP socket for server.
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((server_ip, server_port))


while True:
    # Get user input for the command and any associated filenames
    user_input = input("Enter your command: ")
    command_parts = user_input.split(' ', 2)  # Split input to extract command and filenames

    # Use format_request to format the user input
    formatted_request = format_request(*command_parts)

    # Send the formatted request to the server
    send_request(client_socket, formatted_request)

    # If the command is 'bye', exit the loop
    if command_parts[0] == 'bye':
        break

    if command_parts[0] == 'put':
        try:
            with open(command_parts[1], 'rb') as file:
                data = file.read()
            client_socket.sendall(data)
            print(f"File {command_parts[1]} sent successfully.")
        except Exception as e:
            print(f"Error sending file: {e}")
    # Special handling for 'get' command
    if command_parts[0] == 'get':
        try:
            data = client_socket.recv(4096)
            if data.decode(errors='ignore').startswith('File Not Found'):
                print("File Not Found")
            else:
                with open(command_parts[1], 'wb') as file:
                    file.write(data)
                    print("Initial chunk written, size: {} bytes".format(len(data)))
                print(f"File {command_parts[1]} received successfully.")
        except Exception as e:
            print(f"Error receiving file: {e}")
    else:
        # Receive and print the response from the server for other commands
        response = receive_response(client_socket)
        print("Response from server:", response)

# Close connection if 'break'
client_socket.close()
