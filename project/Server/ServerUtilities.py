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
        "011": "summary",
        "100": "help",
        "111": "bye"
    }.get(opcode, "Invalid")

    if command == "Invalid":
        return command, None

    binary_filenames = parts[1] if len(parts) > 1 else ""
    filenames = [binary_to_string(fname) for fname in binary_filenames.split(' ')] if binary_filenames else None
    return command, filenames


# Handle the client's request based on the command type.
def handle_request(parsed_request, connection_socket):
    command, filenames = parsed_request
    # Implement handling logic based on the command and filenames.
    if command == 'put':
        if filenames:
            filename = filenames[0]
            receive_file(connection_socket, filename)
            send_response(connection_socket, "File received successfully.")
        else:
            send_response(connection_socket, "No file specified.")

    elif command == 'get':
        if filenames and os.path.exists(filenames[0]):
            print(f"File {filenames[0]} found, preparing to send.")  # Debugging print
            send_file(connection_socket, filenames[0])
        else:
            print(f"File {filenames[0]} not found.")  # Debugging print
            send_response(connection_socket, "Error - File Not Found")

    elif command == 'summary':
        summary = "Server Summary:\n"
        # List all files in the server directory
        files = os.listdir('.')
        summary += f"Files on server: {', '.join(files)}\n"
        send_response(connection_socket, summary)

    elif command == 'change':
        if len(filenames) == 2:
            success = rename_file(filenames[0], filenames[1])
            if success:
                send_response(connection_socket, "File renamed successfully.")
            else:
                send_response(connection_socket, "Rename failed. File not found or new filename not provided.")
        else:
            send_response(connection_socket, "Invalid command format for change.")

    elif command == 'help':
        handle_help(connection_socket)

    elif command == 'bye':
        close_connection(connection_socket)
        print("Client disconnected.")
        return False  # Indicate that the connection should be closed

    else:
        send_response(connection_socket, "10000000")

    return True  # Indicate that the server should keep running


# Send a response back to the client.
def send_response(connection_socket, response):
    connection_socket.send(response.encode())

# Function to save the received file
def save_file(filename, file_size, file_data):
    try:
        with open(filename, 'wb') as file:
            file.write(file_data)
        print(f"File {filename} received and saved successfully, size: {file_size} bytes.")
    except Exception as e:
        print(f"Error saving file: {e}")

# Function to receive a file from the client and return filename, file_size, and file_data
def receive_file(connection_socket, filename):
    try:
        print(f"Receiving file: {filename}")
        filename_length = int(connection_socket.recv(5).decode(), 2)
        binary_filename = connection_socket.recv(filename_length).decode()
        data = connection_socket.recv(4096)  # Receive up to 4096 bytes

        with open(binary_to_string(binary_filename), 'wb') as file:
            file.write(data)

        print(f"File {filename} received and saved successfully.")
    except Exception as e:
        print(f"Error receiving file: {e}")


# Function to send a file to the client
def send_file(connection_socket, filename):
    try:
        fileExists = os.path.exists(filename)
        if fileExists:
            # Read the file data
            with open(filename, 'rb') as file:
                data = file.read()
            # Send filename length and filename
            filename_length = format(len(filename), '05b')
            connection_socket.send(filename_length.encode())
            connection_socket.send(string_to_binary(filename).encode())
            # Send file data
            connection_socket.send(data)
            print(f"File {filename} sent to client, size: {len(data)} bytes")
        else:
            print(f"File {filename} not found.")
            # Send error response
            error_response = "Error - File Not Found"
            connection_socket.send(error_response.encode())
    except Exception as e:
        print(f"Error sending file: {e}")


# Function to rename a file on the server (change)
def rename_file(old_filename, new_filename):
    try:
        # Check if the old file exists before attempting to rename
        if os.path.exists(old_filename):
            # Check if the new filename is provided
            if new_filename:
                os.rename(old_filename, new_filename)
                print(f"File {old_filename} renamed to {new_filename} successfully.")
                return True
            else:
                print("New filename not provided. Rename failed.")
                return False
        else:
            print(f"File {old_filename} not found. Rename failed.")
            return False
    except Exception as e:
        print(f"Error renaming file: {e}")
        return False

# Function to handle 'help' command
def handle_help(connection_socket):
    res_code = "110"
    help_message = "Available commands: put, get, summary, change, help, bye"
    help_length = (len(help_message))
    data = format(int(res_code,2),'03b')+format(help_length, '05b')+''.join(format(ord(char), '08b') for char in help_message)
    print(data)
    send_response(connection_socket, data)


def binary_to_string(input_binary):
    binary_values = input_binary.split()
    ascii_characters = [chr(int(binary, 2)) for binary in binary_values]
    return ''.join(ascii_characters)

def string_to_binary(input_string):
    return ' '.join(format(ord(char), '08b') for char in input_string)

# Function to close the connection
def close_connection(connection_socket):
    connection_socket.close()
