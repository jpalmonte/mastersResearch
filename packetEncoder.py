"""
TLEPacketEncoder
ENCODE TLE SECTIONS INTO 32-BYTE DATA PACKET
32-BYTE DATA PACKET FORMATTED IN LITTLE ENDIAN
"""

# ADDRESS OF TLE = 04 B0 00 00

import requests
import numpy as n
from ctypes import *
import tkinter as tk
from datetime import datetime

# INPUT TLE DATA FOR TRANSMISSION TO SATELLITE

# FETCH TLE DATA FROM CELESTRAK
url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"
response = requests.get(url)
data = response.text


def inputSatellite():
    global user_input
    user_input = entry.get().upper() # INPUT NOT CASE SENSITIVE
    root.destroy()

# ERROR FLAGS FOR SATELLITE INPUT GUI    
errorFlag = 1
notFound = 0
noInput = 0

# LOOP UNTIL SATELLITE INPUT IS VALID
while(errorFlag == 1):
    root = tk.Tk()
    root.title("Download TLE Data")
    root.geometry("280x90")

    # CREATE A LABEL AND AN ENTRY FIELD
    label = tk.Label(root, text="Enter satellite name:")
    label.pack()
    entry = tk.Entry(root)
    entry.pack()

    # CREATE A BUTTON TO STORE THE INPUT AND CLOSE THE GUI
    button = tk.Button(root, text="Download TLE", command=inputSatellite)
    button.pack()

    root.bind('<Return>', lambda event: inputSatellite())

    # CONDITIONAL CHECK IF THE SATELLITE INPUT IS NOT VALID OR AVAILABLE
    if notFound == 1:
        text_widget = tk.Text(root, height=100, width=100)
        text_widget.pack()
        text_widget.insert(tk.END, "Satellite not found")
        notFound = 0
    if noInput == 1:
        text_widget = tk.Text(root, height=100, width=100)
        text_widget.pack()
        text_widget.insert(tk.END, "Please enter satellite")
        noInput = 0

    # START THE GUI EVENT LOOP
    root.mainloop()

    # SPLIT THE TLE DATA INTO INDIVIDUAL ENTRIES
    tle_entries = data.split('\n')

    # FILTER OUT ENTRIES FOR TARGET SATELLITE 
    filtered_entries = []
    for i in range(0, len(tle_entries), 3):
        if user_input == '':
            noInput = 1 # SET FLAG IF NO INPUT 
            break
        if user_input == tle_entries[i].strip():
            notFound = 0 # CLEAR NOT FOUND FLAG
            errorFlag = 0 # CLEAR ERROR FLAG
            noInput = 0 # CLEAR NO INPUT FLAG
            filtered_entries.extend(tle_entries[i:i+3])
            break
        else:
            notFound = 1 # SET FLAG IF THE SATELLITE INPUT IS NOT VALID
    
    

# FILTER TARGET SATELLITE TLE DATA
satellite = user_input
lines = data.strip().split("\n")
satellite_tle = []
for i in range(0, len(lines), 3):
    if lines[i].startswith(satellite):
        satellite_tle.append(lines[i:i+3])

# PARSE TLE STRINGS AND EXTRACT VARIABLES
for tle in satellite_tle:
    name = tle[0].strip()  
    line1 = tle[1]
    line2 = tle[2]

    # SPLIT EACH ROW INTO STRINGS
    epoch = float(line1[18:32].strip())
    derivative = line1[33:43].strip()
    drag = line1[54:61].strip()
    inclination = float(line2[8:16].strip())
    raan = float(line2[17:25].strip())
    eccentricity = line2[26:33].strip()
    argPerigee = float(line2[34:42].strip())
    meanAnomaly = float(line2[43:51].strip())
    meanMotion = float(line2[52:63].strip())

# PRINT FOR DEBUGGING
'''print("TLE Data \n")
print('Epoch Year and Julian Date Fraction = ', epoch)
print('1st Derivative of Mean Motion = ', derivative)
print('Drag Term = ', drag)
print('Inclination = ', inclination)
print("Right Ascension of the Ascending Node = ", raan)
print("Eccentricity = ", eccentricity)
print("Argument of Perigee = ", argPerigee)
print("Mean Anomaly = ", meanAnomaly)
print("Mean Motion = ", meanMotion)
'''

# FLOATING POINT CONVERSION TO HEX
def toInt(s):
  cp = pointer(c_float(s))
  fp = cast(cp, POINTER(c_int))
  return fp.contents.value

# ENCODE EPOCH TO HEX 5.5 BYTES 0xNNNNNNNNNNN
EP_int = (int(epoch) << 3) << (6*4)
EP_dec = int(str(round((epoch - int(epoch))*100000000,1)).split(".")[0])
EP = (EP_int + EP_dec) 
#print("Epoch: ", hex(EP))

# ENCODE 1ST DERIVATIVE OF MEAN MOTION TO HEX 4 BYTES 0xNNNNNNNN
DV_sign = derivative.split(".")[0]
DV1 = int(derivative.split(".")[1][0:4])
DV2 = int(derivative.split(".")[1][4:])
DV = (DV1 << 16) + DV2
if(DV_sign != "-"): DV = DV + 0x80000000
#print("1st Derivative of Mean Motion: ", hex(DV))

# ENCODE DRAG TERM TO HEX 3 BYTES 0xNNNNNN
if drag[0] == '-': 
  DT_sign = '-'
  drag = drag[1:]
else: DT_sign = '+'
DT1 = int(drag.split("-")[0])
DT2 = int(drag.split("-")[1])
if(DT_sign == '+'): DT2 = DT2 + 0x8
DT1 = DT1 << 4
DT = DT1 + DT2
#print(hex(DT))

# ENCODE INCLINATION 3 BYTES 0xNNNNNN
IN_int = int(str(inclination).split(".")[0]) << 16
IN_dec = int(str(round((inclination - int(inclination))*10000,4)).split(".")[0])
IN = IN_int + IN_dec
#print("Inclination: ", hex(IN))

# ENCODE RIGHT ASCENSION OF THE ASCENDING NODE 3 BYTES 0xNNNNNN
RN_int = (int(str(raan).split(".")[0]) << 3) << (3*4)
RN_dec = int(str(round((raan - int(raan))*10000,4)).split(".")[0])
RN = RN_int + RN_dec
#print("RAAN: ", hex(RN))

# ENCODE ECCENTRICITY 3 BYETS 0xNNNNNN
EC = int(eccentricity)
#print("Eccentricity: ", hex(EC))

# ENCODE ARGUMENT OF PERIGEE
AP_int = (int(str(argPerigee).split(".")[0]) << 3) << (3*4)
AP_dec = int(str(round((argPerigee - int(argPerigee))*10000,4)).split(".")[0])
AP = AP_int + AP_dec
#print("Argument of Perigee: ", hex(AP))

# ENCODE MEAN ANOMALY
MA_int = int(str(meanAnomaly).split(".")[0]) << 16
MA_dec = int(str(meanAnomaly).split(".")[1])
MA_dec = int(str(round((meanAnomaly - int(meanAnomaly))*10000,4)).split(".")[0])
MA = MA_int + MA_dec
#print("Mean Anomaly: ", hex(MA))

# ENCODE MEAN MOTION
MM = toInt(meanMotion)
#print("Mean Motion: ", hex(MM))

# CREATE DATA PACKET FOR TRANSMISSION
EP_tle = EP << int(26.5*8)
DV_tle = DV << int(22.5*8)
DT_tle = DT << int(19.5*8)
IN_tle = IN << int(16.5*8)
RN_tle = RN << int(13.5*8)
EC_tle = EC << int(10.5*8)
AP_tle = AP << int(7.5*8)
MA_tle = MA << int(4*8)
MM_tle = MM

DATA_PACKET = EP_tle + DV_tle + DT_tle + IN_tle + RN_tle + EC_tle + AP_tle + MA_tle + MM_tle
print("\nEncoded TLE Packet for {}\n{}\n" .format(satellite,hex(DATA_PACKET)))

##################################################################### 

# GENERATE UPLINK COMMAND

UL_DATA1 = hex((DATA_PACKET & 0xFFFFFFFFFFFFFFFF000000000000000000000000000000000000000000000000) >> 24*8).upper()[2:].zfill(16)
UL_DATA2 = hex((DATA_PACKET & 0x0000000000000000FFFFFFFFFFFFFFFF00000000000000000000000000000000) >> 16*8).upper()[2:].zfill(16)
UL_DATA3 = hex((DATA_PACKET & 0x00000000000000000000000000000000FFFFFFFFFFFFFFFF0000000000000000) >> 8*8).upper()[2:].zfill(16)
UL_DATA4 = hex((DATA_PACKET & 0x000000000000000000000000000000000000000000000000FFFFFFFFFFFFFFFF)).upper()[2:].zfill(16)

UL1 = '51 00 31 {} {} {} {} {} {} {} {}'.format(UL_DATA1[0:2], UL_DATA1[2:4], UL_DATA1[4:6], UL_DATA1[6:8], UL_DATA1[8:10], UL_DATA1[10:12], UL_DATA1[12:14], UL_DATA1[14:16])
UL2 = '51 00 32 {} {} {} {} {} {} {} {}'.format(UL_DATA2[0:2], UL_DATA2[2:4], UL_DATA2[4:6], UL_DATA2[6:8], UL_DATA2[8:10], UL_DATA2[10:12], UL_DATA2[12:14], UL_DATA2[14:16])
UL3 = '51 00 33 {} {} {} {} {} {} {} {}'.format(UL_DATA3[0:2], UL_DATA3[2:4], UL_DATA3[4:6], UL_DATA3[6:8], UL_DATA3[8:10], UL_DATA3[10:12], UL_DATA3[12:14], UL_DATA3[14:16])
UL4 = '51 00 34 {} {} {} {} {} {} {} {}'.format(UL_DATA4[0:2], UL_DATA4[2:4], UL_DATA4[4:6], UL_DATA4[6:8], UL_DATA4[8:10], UL_DATA4[10:12], UL_DATA4[12:14], UL_DATA4[14:16])

print('',UL1,'\n',UL2,'\n',UL3,'\n',UL4)

# DOWNLINK COMMAND
DL = '51 00 35 04 B0 00 00 01 00 00 01'

# CREATE GUI TO PRINT UPLINK AND DOWNLINK COMMANDS FOR THE TLE
timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def create_gui():
    lines_of_strings = [
        'Retrieved: ' + timestamp + '\n\n',
        name + '\n',
        line1 + '\n',
        line2 + '\n\n',
        str(hex(DATA_PACKET)) + '\n\n',
        "UL CMD 1 = {} \n".format(UL1),
        "UL CMD 2 = {} \n".format(UL2),
        "UL CMD 3 = {} \n".format(UL3),
        "UL CMD 4 = {} \n".format(UL4),
        "DL COMMAND = {}".format(DL)
    ]

    root = tk.Tk()
    root.title("Uplink & Downlink Commands for {} TLE".format(name))
    root.geometry("600x273")

    text_widget = tk.Text(root, height=14, width=80)
    text_widget.pack()

    # PRINT THE TLE, ENCODED HEX, AND UL/DL COMMANDS
    for line in lines_of_strings:
        text_widget.insert(tk.END, line)

    # CREATE BUTTON TO SAVE TLE FILE INTO TEXT
    def saveTLEtofile():
        filename = satellite + '.txt'
        outputTLE = satellite.rstrip() + '\n' + line1.rstrip() + '\n' + line2.rstrip()
        saveFlag = 1
        
        with open(filename, 'w') as file:
            file.write(outputTLE)

        #save_widget = tk.Text(root, height=1, width=10)
        save_widget = tk.Entry(root, width=100, justify='center')
        save_widget.pack()
        save_widget.insert(tk.END, "TLE saved")
        saveFlag = 0

    saveFlag = 0
    save_button = tk.Button(root, text="Save TLE", command=saveTLEtofile)
    save_button.pack()


    # RUN GUI
    root.mainloop()

create_gui()

# CREATE SAVE BUTTON TO SAVE TLE FILE INTO TEXT




# run "pyinstaller --onefile packetEncoder.py" to create .exe file
