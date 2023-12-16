# Similar to ServerUtilities.py, for message formatting and conversion.
# Include formatRequest, interpretResponse, and conversion functions.

import os  # for getsize() function
from socket import *

'''
# Formats a request to be sent to server based on the given command & filenames
def format_request(command, filename=None, new_filename=None):
    binary_command = string_to_binary(command)
    print("Command in binary:", binary_command)
    request = binary_command
    if filename:
        binary_filename = string_to_binary(filename)
        request += f" {binary_filename}"  # append filename to the request.
    if new_filename:  # if new filename provided -> rename
        binary_new_filename = string_to_binary(new_filename)
        request += f" {binary_new_filename}"  # append new filename to the request.
    return request  # return the formatted request
'''

def format_request(command, filename=None, new_filename=None):
    opcode = {
        "put": "000",
        "get": "001",
        "change": "010",
        "help": "011",
        "bye": "111"
    }.get(command, "")

    if not opcode:
        return "Invalid command"

    request = opcode
    if filename:
        binary_filename = string_to_binary(filename)
        request += f" {binary_filename}"
    if new_filename:
        binary_new_filename = string_to_binary(new_filename)
        request += f" {binary_new_filename}"

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
    # receive up to 1024 bytes from server, decode it from bytes to a string.
    response = client_socket.recv(1024).decode()
    return response  # return the decoded response.

