"""
TLEPacketEncoder
ENCODE TLE SECTIONS INTO 32-BYTE DATA PACKET
32-BYTE DATA PACKET FORMATTED IN LITTLE ENDIAN
"""

# ADDRESS OF TLE = 04 B0 00 00

import numpy as n
from ctypes import *

# INPUT TLE DATA FOR TRANSMISSION TO SATELLITE

# DIWATA-2B TLE 6/13/2023
epoch = 23163.90064120
derivative = '.00001607'
drag = '15865-3'
inclination = 98.0225
raan = 307.7835
eccentricity = '0009791'
argPerigee = 167.9441
meanAnomaly = 192.1513
meanMotion = 14.93416279
epoch_original = epoch

print("Sample TLE Data \n")
print('Epoch Year and Julian Date Fraction = ', epoch)
print('1st Derivative of Mean Motion = ', derivative)
print('Drag Term = ', drag)
print('Inclination = ', inclination)
print("Right Ascension of the Ascending Node = ", raan)
print("Eccentricity = ", eccentricity)
print("Argument of Perigee = ", argPerigee)
print("Mean Anomaly = ", meanAnomaly)
print("Mean Motion = ", meanMotion)

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
print("\nEncoded TLE Packet \n\n{}\n" .format(hex(DATA_PACKET)))

##################################################################### 

# GENERATE UPLINK COMMAND

UL_DATA1 = hex((DATA_PACKET & 0xFFFFFFFFFFFFFFFF000000000000000000000000000000000000000000000000) >> 24*8).upper()
UL_DATA2 = hex((DATA_PACKET & 0x0000000000000000FFFFFFFFFFFFFFFF00000000000000000000000000000000) >> 16*8).upper()
UL_DATA3 = hex((DATA_PACKET & 0x00000000000000000000000000000000FFFFFFFFFFFFFFFF0000000000000000) >> 8*8).upper()
UL_DATA4 = hex((DATA_PACKET & 0x000000000000000000000000000000000000000000000000FFFFFFFFFFFFFFFF)).upper()

UL1 = '51 00 31 {} {} {} {} {} {} {} {}'.format(UL_DATA1[2:4], UL_DATA1[4:6], UL_DATA1[6:8], UL_DATA1[8:10], UL_DATA1[10:12], UL_DATA1[12:14], UL_DATA1[14:16], UL_DATA1[16:18])
UL2 = '51 00 32 {} {} {} {} {} {} {} {}'.format(UL_DATA2[2:4], UL_DATA2[4:6], UL_DATA2[6:8], UL_DATA2[8:10], UL_DATA2[10:12], UL_DATA2[12:14], UL_DATA2[14:16], UL_DATA2[16:18])
UL3 = '51 00 33 {} {} {} {} {} {} {} {}'.format(UL_DATA3[2:4], UL_DATA3[4:6], UL_DATA3[6:8], UL_DATA3[8:10], UL_DATA3[10:12], UL_DATA3[12:14], UL_DATA3[14:16], UL_DATA3[16:18])
UL4 = '51 00 34 {} {} {} {} {} {} {} {}'.format(UL_DATA4[2:4], UL_DATA4[4:6], UL_DATA4[6:8], UL_DATA4[8:10], UL_DATA4[10:12], UL_DATA4[12:14], UL_DATA4[14:16], UL_DATA4[16:18])

print('',UL1,'\n',UL2,'\n',UL3,'\n',UL4)

# DOWNLINK COMMAND
DL = '51 00 35 04 B0 00 00 01 00 00 01'