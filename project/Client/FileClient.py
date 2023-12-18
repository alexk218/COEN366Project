import os
import ipaddress
from socket import *

OPCODES = {
    "put": "000",
    "get": "001",
    "change": "010",
    "summary": "011",
    "help": "100",
    "bye": "111"
}

def is_valid_ip(ip):
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ipaddress.AddressValueError:
        return False

def string_to_binary(input_string):
    return ' '.join(format(ord(char), '08b') for char in input_string)

def binary_to_string(input_binary):
    binary_values = input_binary.split()
    ascii_characters = [chr(int(binary, 2)) for binary in binary_values]
    return ''.join(ascii_characters)

def format_request(command, filename=None, new_filename=None):
    opcode = OPCODES.get(command, "")

    if not opcode:
        return "Invalid command"

    request = opcode
    if filename:
        binary_filename = string_to_binary(filename)
        filename_length = format(len(filename), '05b')
        request += f" {filename_length} {binary_filename}"
    if new_filename:
        binary_new_filename = string_to_binary(new_filename)
        new_filename_length = format(len(new_filename), '05b')
        request += f"{new_filename_length} {binary_new_filename}"

    return request

def send_request(client_socket, request):
    print(f"Sending to server: {request}")
    client_socket.send(request.encode())

def connect_to_server(ip, port):
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((ip, port))
    return client_socket

def process_put_command(client_socket, filename):
    try:
        # Check if the file exists
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Error: File {filename} not found. Please enter a valid filename.")

        # Validate filename length
        if len(filename) > 31:
            raise ValueError("Error: Filename length exceeds the limit. Please enter a valid filename.")

        # Get file size
        file_size = os.path.getsize(filename)

        # Validate file size
        if file_size > (2 ** 32) - 1:
            raise ValueError("Error: File size exceeds the limit. Please enter a valid filename.")

        # Format filename length and file size
        filename_length = format(len(filename), '05b')
        file_size_binary = format(file_size, '032b')

        # Form the request
        request = f"000 {filename_length} {string_to_binary(filename)} {file_size_binary}"

        # Send the request
        send_request(client_socket, request)

        # Read and send the file data in chunks
        with open(filename, 'rb') as file:
            chunk_size = 1024
            while True:
                data_chunk = file.read(chunk_size)
                if not data_chunk:
                    break
                client_socket.sendall(data_chunk)

        # Receive the response from the server
        response = receive_response(client_socket)
        print(f"Response from server: {response}")

        # Check if the response code is '000'
        if response[:3] == '000':
            print(f"File {filename} sent successfully.")
        else:
            print(f"Error: Put request failed. Server response: {response}")

    except Exception as e:
        print(f"Error processing 'put' command: {e}")

def process_get_command(command_parts, client_socket):
    try:
        # Extract filename from the command_parts
        filename = command_parts[1]

        # Opcode for "get" command
        opcode = "001"

        # Encode Filename Length (FL) in 5 bits
        filename_length = format(len(filename), '05b')

        # Form the request
        formatted_request = f"{opcode} {filename_length} {string_to_binary(filename)}"

        # Send the formatted request to the server
        send_request(client_socket, formatted_request)

        # Receive the response from the server
        response = receive_response(client_socket)

        # Check if the response code is 001
        if response[:3] == '001':
            # Decode the response message
            filename_length = int(response[3:8], 2)
            filename = binary_to_string(response[8:8 + filename_length])
            file_size = int(response[8 + filename_length:8 + filename_length + 32], 2)

            print(f"Received file: {filename}, Size: {file_size} bytes")

            # Receive and process the file data
            file_data = b""  # Initialize an empty byte string to store the file data

            while len(file_data) < file_size:
                # Receive a chunk of data from the server
                chunk = client_socket.recv(1024)

                if not chunk:
                    break  # Break the loop if no more data is received

                file_data += chunk

            # Save the received file data to a local file
            with open(filename, 'wb') as file:
                file.write(file_data)

            print(f"File {filename} received successfully.")
        else:
            print(f"Error: Get request failed. Server response: {response}")

    except Exception as e:
        print(f"Error processing 'get' command: {e}")

def process_help_command(client_socket):
    try:
        # Send the help request to the server
        code = "10000000"
        binary_code = format(int(code, 2), '08b')  # Convert to binary
        send_request(client_socket, binary_code)

        # Receive the response from the server
        response = receive_response(client_socket)

        # Check if the response code is 110
        if response[:3] == '110':
            # Decode the response message
            length = int(response[3:8], 2)
           # print(f"Response: {response}, Type: {type(response)}")
            help_data = binary_to_string(response[8:8 + length])

            print(f"Help Data: {help_data}")
        else:
            print("Error: Help request failed. Check the server response.")
    except Exception as e:
        print(f"Error processing 'help' command: {e}")

def receive_response(client_socket):
    # Receive the first byte to check the left-most three bits
    response_code = client_socket.recv(1024).decode()

    # Check if the left-most three bits are '000' for correct put or change request
    if response_code[:3] == '000':
        print("Correct put or change request.")

    # Check if the left-most three bits are '001' for correct get request
    if response_code[:3] == '001':
        return response_code
    
    elif response_code[:3] == '110':
        return response_code
        # If the left-most three bits are not '001', assume a regular response
        # You might want to handle this case differently based on your application
    return response_code

def binary_to_string(input_binary):
    binary_values = input_binary.split()
    # Ensure that binary_values is a list of strings
    ascii_characters = [chr(int(binary, 2)) for binary in binary_values]
    return ''.join(ascii_characters)


def main():
    while True:
        try:
            # Get user input for the server IP and port
            server_ip = input("Enter the server IP address: ")

            # Validate server IP
            if not is_valid_ip(server_ip):
                raise ValueError("Invalid IP address. Please enter a valid IPv4 address.")

            while True:
                server_port_input = input("Enter the server port number: ")

                try:
                    # Validate and convert the port number to an integer
                    server_port = int(server_port_input)

                    if not (0 < server_port < 65535):
                        raise ValueError("Invalid port number. Please enter a number between 1 and 65534.")

                    break  # Exit the port input loop if valid
                except ValueError:
                    print("Invalid port number. Please enter a valid integer.")

            # Create a TCP socket for the server
            client_socket = socket(AF_INET, SOCK_STREAM)

            # Attempt to connect to the server
            client_socket.connect((server_ip, server_port))

            break  # Exit the loop if connection is successful

        except ValueError as ve:
            print(f"Error: {ve}")
        except ConnectionRefusedError:
            print(f"Connection refused. Please check the server IP and port.")
        except Exception as e:
            print(f"Error: {e}")

    while True:
        try:
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

                # Process different commands
                if command_parts[0] == 'put':
                    process_put_command(client_socket, command_parts[1])
                elif command_parts[0] == 'get':
                    process_get_command(command_parts, client_socket)
                elif command_parts[0] == 'help':
                    process_help_command(client_socket)
                else:
                    # For other commands, simply receive and print t12he response
                    response = receive_response(client_socket)
                    print(response)

        except ValueError as ve:
            print(f"Error: {ve}")
        except ConnectionRefusedError:
            print(f"Connection refused. Please check the server IP and port.")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Close the socket if it was created
            if 'client_socket' in locals():
                client_socket.close()

if __name__ == "__main__":
    main()
