import os
from socket import *

def parse_request(request):
    opcode, *rest = request.split(' ', 1)

    command = {
        "000": "put",
        "001": "get",
        "010": "change",
        "011": "summary",
        "100": "help",
        "111": "bye"
    }.get(opcode, "Invalid")

    filenames = [binary_to_string(fname) for fname in rest[0].split(' ')] if rest else None

    return command, filenames

def handle_request(parsed_request, connection_socket):
    command, filenames = parsed_request

    print(f"Received from client: {command} {filenames}")

    if command == 'put':
        handle_put_command(filenames, connection_socket)
    elif command == 'get':
        handle_get_command(filenames, connection_socket)
    elif command == 'summary':
        handle_summary_command(connection_socket)
    elif command == 'change':
        handle_change_command(filenames, connection_socket)
    elif command == 'help':
        handle_help_command(connection_socket)
    elif command == 'bye':
        handle_bye_command(connection_socket)
        return False
    else:
        send_response(connection_socket, "10000000")

    return True

def handle_put_command(filenames, connection_socket):
    if filenames:
        filename = filenames[0]
        receive_file(connection_socket, filename)
        send_response(connection_socket, "File received successfully.")
    else:
        send_response(connection_socket, "No file specified.")

def handle_get_command(filenames, connection_socket):
    if filenames and os.path.exists(filenames[0]):
        print(f"File {filenames[0]} found, preparing to send.")
        send_file(connection_socket, filenames[0])
    else:
        print(f"File {filenames[0]} not found.")
        send_response(connection_socket, "Error - File Not Found")

def handle_summary_command(connection_socket):
    summary = "Server Summary:\n"
    files = os.listdir('.')
    summary += f"Files on server: {', '.join(files)}\n"
    send_response(connection_socket, summary)

def handle_change_command(filenames, connection_socket):
    if len(filenames) == 2:
        success = rename_file(filenames[0], filenames[1])
        if success:
            send_response(connection_socket, "File renamed successfully.")
        else:
            send_response(connection_socket, "Rename failed. File not found or new filename not provided.")
    else:
        send_response(connection_socket, "Invalid command format for change.")

def handle_help_command(connection_socket):
    try:
        res_code = "110"
        help_message = "Available commands: put, get, summary, change, help, bye"
        help_length = len(help_message)
        
        # Ensure the length does not exceed 31 characters
        if help_length > 31:
            help_length = 31

        # Form the response message
        data = format(int(res_code, 2), '03b') + format(help_length, '05b') + ''.join(
            format(ord(char), '08b') for char in help_message[:help_length])
        print(data)
        # Send the response
        send_response(connection_socket, data)

    except Exception as e:
        print(f"Error handling 'help' command: {e}")


def handle_bye_command(connection_socket):
    close_connection(connection_socket)
    print("Client disconnected.")

def send_response(connection_socket, response):
    connection_socket.send(response.encode())

def receive_file(connection_socket, filename):
    try:
        print(f"Receiving file: {filename}")
        filename_length = int(connection_socket.recv(5).decode(), 2)
        binary_filename = connection_socket.recv(filename_length).decode()
        data = connection_socket.recv(4096)

        with open(binary_to_string(binary_filename), 'wb') as file:
            file.write(data)

        print(f"File {filename} received and saved successfully.")
    except Exception as e:
        print(f"Error receiving file: {e}")

def send_file(connection_socket, filename):
    try:
        file_exists = os.path.exists(filename)
        if file_exists:
            with open(filename, 'rb') as file:
                data = file.read()

            filename_length = format(len(filename), '05b')
            connection_socket.send(filename_length.encode())
            connection_socket.send(string_to_binary(filename).encode())
            connection_socket.send(data)
            print(f"File {filename} sent to client, size: {len(data)} bytes")
        else:
            print(f"File {filename} not found.")
            error_response = "Error - File Not Found"
            connection_socket.send(error_response.encode())
    except Exception as e:
        print(f"Error sending file: {e}")

def rename_file(old_filename, new_filename):
    try:
        if os.path.exists(old_filename):
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

def binary_to_string(input_binary):
    binary_values = input_binary.split()
    ascii_characters = [chr(int(binary, 2)) for binary in binary_values]
    return ''.join(ascii_characters)

def string_to_binary(input_string):
    return ' '.join(format(ord(char), '08b') for char in input_string)

def close_connection(connection_socket):
    connection_socket.close()

if __name__ == "__main__":
    # Connecting to client
    server_ip = '127.0.0.1'  # listen on all interfaces
    server_port = 12000  # server port is fixed

    server_socket=socket(AF_INET, SOCK_STREAM)
    server_socket.bind((server_ip, server_port))

    # Server begins listening for incoming TCP requests.
    server_socket.listen(1)
    print('The server is ready to receive')

    while True:
        connection_socket, addr = server_socket.accept()
        print(f"Connection established with {addr}")

        keep_alive = True
        while keep_alive:
            client_request = connection_socket.recv(1024).decode()
            if not client_request:
                break

            print("Received from client:", client_request)
            command, filenames = parse_request(client_request)
            keep_alive = handle_request((command, filenames), connection_socket)

        connection_socket.close()
