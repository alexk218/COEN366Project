# Similar to ServerUtilities.py, for message formatting and conversion.
# Include formatRequest, interpretResponse, and conversion functions.

import os 
from socket import *

# Formats a request to be sent to server based on the given command & filenames
def format_request(command, filename=None, new_filename=None):
    opcode = {
        "put": "000",
        "get": "001",
        "change": "010",
        "summary": "011",
        "help": "100",
        "bye": "111"
    }.get(command, "")

    if not opcode:
        return "Invalid command"

    request = opcode
    if filename:
        binary_filename = string_to_binary(filename)
        filename_length = format(len(filename), '05b')  # Encode filename length in 5 bits
        request += f" {filename_length} {binary_filename}"
       # print({request})
    if new_filename:
        binary_new_filename = string_to_binary(new_filename)
        new_filename_length = format(len(new_filename), '05b')
        request += f"{new_filename_length} {binary_new_filename}"

    return request


def string_to_binary(input_string):
    return ' '.join(format(ord(char), '08b') for char in input_string)

def binary_to_string(input_binary):
    binary_values = input_binary.split()
    ascii_characters = [chr(int(binary, 2)) for binary in binary_values]
    return ''.join(ascii_characters)

# send the formatted request to server
def send_request(client_socket, request):
    client_socket.send(request.encode())

# Receive response from server & return it.
def receive_response(client_socket):
    # receive the first byte to check the left-most three bits
    response_code = client_socket.recv(1).decode()

    # Check if the left-most three bits are '110'
    if response_code[:3] == '110':
        # Receive and decode the rest of the message
        response_data = client_socket.recv(1023).decode()
        return response_data
    else:
        # If the left-most three bits are not '110', assume a regular response
        # You might want to handle this case differently based on your application
        return response_code

