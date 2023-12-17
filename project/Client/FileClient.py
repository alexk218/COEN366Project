# Main client script to interact with the server.
# Functions for user input processing and server communication.

import os
import ipaddress
from socket import *
from ClientUtilities import *

def is_valid_ip(ip):
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ipaddress.AddressValueError:
        return False

# # Enter server's IP address and port #.
# # Loop until the user enters a valid IP address
# while True:
#     server_ip = input("Enter the server IP address: ")
#     if is_valid_ip(server_ip):
#         break
#     else:
#         print("Invalid IP address format. Please enter a valid IPv4 address.")

# # Loop until the user enters a valid port number
# while True:
#     try:
#         server_port_input = input("Enter the server port number: ")
#         server_port = int(server_port_input)

#         # Check if the entered port number is in a valid range
#         if 0 < server_port < 65536:
#             break
#         else:
#             print("Invalid port number. Please enter a port number between 1 and 65535.")
#     except ValueError:
#         print("Invalid port number. Please enter a valid integer for the port.")

server_ip = "127.0.0.1"
server_port_input = "12000"
try:
    # Validate and convert the port number to an integer
    server_port = int(server_port_input)

    # Check if the entered IP is a valid format
    if not server_ip or not is_valid_ip(server_ip):
        print("Invalid server IP address.")
        exit()

    # Check if the entered port number is in a valid range
    if not (0 < server_port < 65536):
        print("Invalid port number. Please enter a port number between 1 and 65535.")
        exit()

    # Create a TCP socket for the server
    client_socket = socket(AF_INET, SOCK_STREAM)

    # Attempt to connect to the server
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

        # Check if the file exists before forming the request for 'put' command
        if command_parts[0] == 'put':
            while True:
                try:
                    filename = command_parts[1]
                    if os.path.exists(filename):
                        command_parts[1] = filename
                        # Form and send the request
                        formatted_request = format_request(command_parts[0], filename)
                        send_request(client_socket, formatted_request)

                        # Read and send the file data
                        with open(filename, 'rb') as file:
                            data = file.read()
                        client_socket.sendall(data)

                        print(f"File {filename} sent successfully.")
                        break  # Exit the loop if the file exists and the request is sent
                    else:
                        print(f"Error: File {filename} not found. Please enter a valid filename.")
                        filename = input("Enter a valid filename: ")  # Prompt the user again
                except Exception as e:
                    print(f"Error sending file: {e}")
        else:
            # For other commands, simply send the formatted request
            send_request(client_socket, format_request(*command_parts))


        # Special handling for 'get' command
        if command_parts[0] == 'get':
            try:
                data = client_socket.recv(4096)
                response_code, response_message = data.decode().split(' ', 1)

                if response_code == '011':
                    print(f"Error: {response_message}")
                else:
                    if response_message.startswith('File Not Found'):
                        print("File Not Found")
                    else:
                        with open(command_parts[1], 'wb') as file:
                            file.write(data[3:])
                        print(f"File {command_parts[1]} received successfully.")
            except Exception as e:
                print(f"Error receiving file: {e}")
        else:
            # Receive and print the response from the server for other commands
            
            response = receive_response(client_socket)
            
            print(response)
                
except ValueError:
    print("Invalid port number. Please enter a valid integer for the port.")
except ConnectionRefusedError:
    print(f"Connection to {server_ip}:{server_port} refused. Please check the server IP and port.")
except Exception as e:
    print(f"Error: {e}")
finally:
    # Close the socket if it was created
    if 'client_socket' in locals():
        client_socket.close()
