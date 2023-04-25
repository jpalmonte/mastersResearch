import socket

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 8100  # Port to listen on (non-privileged ports are > 1023)

# LISTEN TO KISS PORT OF AX.25 HS SOUNDMODEM
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print('Connected!')
    data = s.recv(108).hex()

appendedFrame = len(data) - 212
print('Number of Appended Frames: {} bytes' .format(int(appendedFrame/2)))
DATA_PACKET_KISS = data[48:112+appendedFrame].upper()
print('Original Data with Appended Frames \n',DATA_PACKET_KISS)
print('Data Length: {} bytes'.format(int(len(DATA_PACKET_KISS)/2)))

# REMOVE APPENDED TRANSPOSED FRAME ESCAPE BY KISS PROTOCOL I.E. CHANGE DBDD TO DB
DATA_PACKET_DBDD = ''
DATA_PACKET_KISS = DATA_PACKET_KISS.split('DBDD')
for i in range(len(DATA_PACKET_KISS)):
    if(i == len(DATA_PACKET_KISS) - 1):
        DATA_PACKET_DBDD = DATA_PACKET_DBDD + DATA_PACKET_KISS[i]
        break
    DATA_PACKET_DBDD = DATA_PACKET_DBDD + DATA_PACKET_KISS[i] + 'DB'

# REMOVE APPENDED TRANSPOSED FRAME END BY KISS PROTOCOL I.E. CHANGE C000 TO C0
DATA_PACKET_C000 = ''
DATA_PACKET_DBDD = DATA_PACKET_DBDD.split('C000')
for j in range(len(DATA_PACKET_DBDD)):
    if(j == len(DATA_PACKET_DBDD) - 1):
        DATA_PACKET_C000 = DATA_PACKET_C000 + DATA_PACKET_DBDD[j]
        break
    DATA_PACKET_C000 = DATA_PACKET_C000 + DATA_PACKET_DBDD[j] + 'C0'

DATA_PACKET = DATA_PACKET_C000

print('Corrected Data \n', DATA_PACKET)
print('Data Length: {} bytes'.format(int(len(DATA_PACKET)/2)))

DATA_PACKET = (int(DATA_PACKET,16)) # CONVERT TO INT FOR PACKET DECODER
print(hex(DATA_PACKET))