import socket
import asyncio

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 8100  # Port to listen on (non-privileged ports are > 1023)
'''
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print('Connected!')
    data = s.recv(108).hex()

print(data)
'''
data = 'c0004a4736594257304c4f52414d4f303ef0fff0ff0000012d225b1d5d2800124e3087f4b3318f78302c90017d3680c190ea10dbdd4177feabffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffc0'

print(len(data))
print(data[0:48])
appendedFrame = len(data) - 212
print(appendedFrame)
DATA_PACKET = data[48:112+appendedFrame]
print(DATA_PACKET)
# SEARCH FOR DBDD AND C000 
# GET ITS INDEX
# REPLACE DBDD WITH DB AND C000 WITH C0