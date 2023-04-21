import socket
import asyncio

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 8100  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print('Connected!')
    data = s.recv(108).hex()

print(data)

