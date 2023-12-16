# Combines message processing and conversion functionalities.
# Functions like parseRequest, createResponse, stringToBinary, and binaryToString

import os

def parse_request(request):
    parts = request.split(' ', 1)  # Split only on the first space.
    opcode = parts[0]
    # Decode the opcode to determine the command
    command = {
        "000": "put",
        "001": "get",
        "010": "change",
        "011": "help",
        "111": "bye"
    }.get(opcode, "Invalid")

    if command == "Invalid":
        return command, None

    binary_filenames = parts[1] if len(parts) > 1 else ""
    filenames = [binary_to_string(fname) for fname in binary_filenames.split('  ')] if binary_filenames else None
    return command, filenames


# Handle the client's request based on the command type.
def handle_request(parsed_request, connection_socket):
    command, filenames = parsed_request
    # Implement handling logic based on the command and filenames.
    if command == 'put':
        if filenames:
            receive_file(connection_socket, filenames[0])
            send_response(connection_socket, "File received successfully.")
        else:
            send_response(connection_socket, "No file specified.")

    elif command == 'get':
        if filenames and os.path.exists(filenames[0]):
            send_file(connection_socket, filenames[0])
        else:
            send_response(connection_socket, "File not found.")

    elif command == 'summary':
        summary = "Server Summary:\n"
        # List all files in the server directory
        files = os.listdir('.')
        summary += f"Files on server: {', '.join(files)}\n"
        send_response(connection_socket, summary)

    elif command == 'change':
        if len(filenames) == 2 and os.path.exists(filenames[0]):
            rename_file(filenames[0], filenames[1])
            send_response(connection_socket, "File renamed successfully.")
        else:
            send_response(connection_socket, "Rename failed. File not found or new filename not provided.")

    elif command == 'help':
        handle_help(connection_socket)

    elif command == 'bye':
        close_connection(connection_socket)
        return False  # Indicate that the connection should be closed

    else:
        send_response(connection_socket, "Invalid command.")

    return True  # Indicate that the server should keep running

# Send a response back to the client.
def send_response(connection_socket, response):
    connection_socket.send(response.encode())

# Function to receive a file from the client and save it
def receive_file(connection_socket, filename):
    with open(filename, 'wb') as file:
        while True:
            data = connection_socket.recv(1024)
            if not data:
                break
            file.write(data)

# Function to send a file to the client
def send_file(connection_socket, filename):
    with open(filename, 'rb') as file:
        data = file.read()
    connection_socket.sendall(data)

# Function to rename a file on the server
def rename_file(old_filename, new_filename):
    os.rename(old_filename, new_filename)

# Function to handle 'help' command
def handle_help(connection_socket):
    help_message = "Available commands: put, get, summary, change, help, bye"
    send_response(connection_socket, help_message)

def binary_to_string(input_binary):
    binary_values = input_binary.split()
    ascii_characters = [chr(int(binary, 2)) for binary in binary_values]
    return ''.join(ascii_characters)

def string_to_binary(input_string):
    return ' '.join(format(ord(char), '08b') for char in input_string)

# Function to close the connection
def close_connection(connection_socket):
    connection_socket.close()
