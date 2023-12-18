from socket import *
from ServerUtilities import *
import logging

# Configure the logging module
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#open server
# Connecting to client
server_ip = '127.0.0.1'  # server port is fixed
server_port = 12010  # server port is fixed

server_socket=socket(AF_INET, SOCK_STREAM)
server_socket.bind((server_ip, server_port))
# Server begins listening for incoming TCP requests.
server_socket.listen(1)
print('The server is ready to receive')

# Create a TCP socket for the server
client_socket = socket(AF_INET, SOCK_STREAM)

# Attempt to connect to the server
client_socket.connect((server_ip, server_port))
client_socket.accept()
#

res_code = "110"
help_message = "Available commands: put, get, summary, change, help, bye"
help_length = len(help_message)
data = f"{res_code}{len(help_message):05b}{' '.join(format(ord(char), '08b') for char in help_message)}"
datae = data.encode()
server_socket.send(datae)

# Receive the first byte to check the left-most three bits
response_code = client_socket.recv(1).decode()
logger.info(f"Server listening on {response_code[:3]}")


# # Check if the left-most three bits are '000' for correct put or change request
# if response_code[:3] == '000':
#     print("Correct put or change request.")

# # Check if the left-most three bits are '001' for correct get request
# if response_code[:3] == '001':
#     # Receive and decode the rest of the message
#     response_data = client_socket.recv(1023).decode()
#     return response_data

# elif response_code[:3] == '110':
#     response_data = client_socket.recv(1023).decode()
#     return response_data