
import socket
import numpy as np
from ctypes import *
import tkinter as tk
import time
import threading
from datetime import datetime
from mttkinter import mtTkinter as mtk


def receiveTLE(gui):
    while True:
        
        HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
        PORT = 8100  # Port to listen on from HS soundmodem(non-privileged ports are > 1023)

        # LISTEN TO KISS PORT OF AX.25 HS SOUNDMODEM
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print('Connected!')
            data = s.recv(108).hex()

        appendedFrame = len(data) - 212
        DATA_PACKET_KISS = data[48:112+appendedFrame].upper()

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

        DATA_PACKET = (int(DATA_PACKET,16)) # CONVERT TO INT FOR PACKET DECODER

        #DATA_PACKET = 0x2d4cc43a2bf800004d70302ab620105a907f9002a682788c911900c0416ef65a

        #########################################################################################################

        # DECODE 32-BYTE DATA PACKET INTO TLE SECTIONS 

        # MASKS TO GET SPECIFIC SECTION OF DATA PACKET
        EP_mask = 0xFFFFFFFFFFF00000000000000000000000000000000000000000000000000000
        DV_mask = 0x00000000000FFFFFFFF000000000000000000000000000000000000000000000
        DT_mask = 0x0000000000000000000FFFFFF000000000000000000000000000000000000000
        IN_mask = 0x0000000000000000000000000FFFFFF000000000000000000000000000000000
        RN_mask = 0x0000000000000000000000000000000FFFFFF000000000000000000000000000
        EC_mask = 0x0000000000000000000000000000000000000FFFFFF000000000000000000000
        AP_mask = 0x0000000000000000000000000000000000000000000FFFFFF000000000000000
        MA_mask = 0x0000000000000000000000000000000000000000000000000FFFFFFF00000000
        MM_mask = 0x00000000000000000000000000000000000000000000000000000000FFFFFFFF


        print("TLE Packet = {} \n" .format(hex(DATA_PACKET)))

        # GET EPOCH YEAR AND JULIAN DAY FRACTION
        EP = (DATA_PACKET & EP_mask) >> int(26.5*8)
        #print(hex(EP))

        # GET 1ST DERIVATIVE OF MEAN MOTION
        DV = (DATA_PACKET & DV_mask) >> int(22.5*8)
        #print(hex(DV))

        # GET DRAG TERM
        DT = (DATA_PACKET & DT_mask) >> int(19.5*8)
        #print(hex(DT))

        # GET INCLINATION
        IN = (DATA_PACKET & IN_mask) >> int(16.5*8)
        #print(hex(IN))

        # GET RIGHT ASCENSION OF THE ASCENDING NODE 
        RN = (DATA_PACKET & RN_mask) >> int(13.5*8)
        #print(hex(RN))

        # GET ECCENTRICITY
        EC = (DATA_PACKET & EC_mask) >> int(10.5*8)
        #print(hex(EC))

        # GET ARGUMENT OF PERIGEE
        AP = (DATA_PACKET & AP_mask) >> int(7.5*8)
        #print(hex(AP))

        # GET MEAN ANOMALY
        MA = (DATA_PACKET & MA_mask) >> int(4*8)
        #print(hex(MA))

        # GET MEAN MOTION
        MM = (DATA_PACKET & MM_mask)
        #print(hex(MM))

        ### CONVERT INTO TLE DATA FORMAT

        # CONVERT HEX TO FLOATING POINT
        def toFloat(s):
            cp = pointer(c_int(s))
            fp = cast(cp, POINTER(c_float))
            str_value = "{:.8f}".format(fp.contents.value)
            return float(str_value)

        def getDecimal(s):
            for i in np.array([1,10,100,1000,10000]):
                if(s % i == s):
                    return(s/i)


        # EPOCH YEAR AND JULIAN DATE FRACTION
        EP_int = ((EP & 0xFFFF8000000) >> 3) >> (6*4)
        EP_dec = EP & 0x00007FFFFFF
        epoch = "{:.8f}".format(int(EP_int) + int(EP_dec) / 1e8)
        #print('Epoch Year and Julian Date Fraction = ', epoch)

        # 1ST DERIVATIVE OF MEAN MOTION
        DV_sign = '-'
        if(DV & 0x80000000 == 0x80000000): 
            DV = DV - 0x80000000
            DV_sign = '+'
        DV1 = (DV >> 16) / 1e4
        DV2 = (DV & 0x0000FFFF) / 1e8
        derivative = "{:.8f}".format(round(DV1 + DV2,8))
        if (DV_sign == '-') : derivative = DV_sign + str(derivative)[1:]
        else: derivative = str(derivative)[1:]
        #print('1st Derivative of Mean Motion = ', derivative)

        # DRAG TERM
        DT1 = DT >> 4
        for pad in range(5 - len(str(DT1))): # PADS ZEROS TO SUPPORT FOR DRAG TERMS LESS THAN 5 DIGITS 
            DT1 = '0' + str(DT1)
        DT2 = DT & 0x00000F
        #DT_sign = '-'
        if(DT2 & 0x8 == 0x8):
            DT2 = DT2 - 0x8
            #DT_sign = '+'
            drag = str(DT1) + '-' + str(DT2)
        else: drag = '-' + str(DT1) + '-' + str(DT2)
        #drag = DT_sign + str(DT1) + '-' + str(DT2)
        #print('Drag Term = ', drag)

        # INCLINATION
        IN_int = IN >> 16
        IN_dec = (IN & 0x00FFFF) / 1e4
        inclination = "{:.4f}".format(IN_int + IN_dec)
        #print('Inclination = ', inclination)

        # RIGHT ASCENSION OF THE ASCENDING NODE 
        RN_int = ((RN & 0xFF8000) >> 3) >> (3*4)
        RN_dec = (RN & 0x007FFF) / 1e4
        raan = "{:.4f}".format(RN_int + RN_dec)
        #print("Right Ascension of the Ascending Node = ", raan)

        # ECCENTRICITY
        eccentricity = "{:.7f}".format(EC / 1e7)
        #print("Eccentricity = ", eccentricity) # ACTUAL VALUE WITH DECIMAL POINT
        #print("Eccentricity = ", str(eccentricity)[2:]) # DECIMAL POINT ASSUMED

        # ARGUMENT OF PERIGEE
        AP_int = ((AP & 0xFF8000) >> 3) >> (3*4)
        AP_dec = (AP & 0x007FFF) / 1e4
        argPerigee = "{:.4f}".format(AP_int + AP_dec)
        #print("Argument of Perigee = ", argPerigee)

        # MEAN ANOMALY
        MA_int = MA >> 16
        MA_dec = (MA & 0x000FFFF) / 1e4
        meanAnomaly = "{:.4f}".format(MA_int + MA_dec)
        #print("Mean Anomaly = ", meanAnomaly)

        # MEAN MOTION
        meanMotion = toFloat(MM)
        meanMotion = "{:.8f}".format(meanMotion)
        #print("Mean Motion = ", meanMotion)


        #########################################################################################################
    

        # OUTPUT DECODED TLE INTO TLE FILE FOR GPREDICT

        ### SUPPORTING FUNCTIONS

        # APPEND INTO STRING AT A SPECIFIC INDEX 
        def insertData(string, data, index):
            return string[:index] + data + string[index:]

        # RETURN CHECKSUM MODULO 10
        def checkSum(digit):
            checksum = 0
            for x in digit:
                if x == '-':
                    checksum = checksum + 1
                if x.isdigit():
                    checksum = checksum + int(x)
            return checksum%10

        ### ABRITARY CONSTANTS FOR DIWATA-2B

        # LINE 1
        satelliteName = 'DIWATA-2B'
        satelliteCatalog = 43678
        classification = 'U'
        intDesignatorYear = 18084
        intDesignatorPiece = 'H'
        secondDerivative = '00000+0'
        ephemeris = 0
        elementSetNumber = 999 # ARBRITARY NUMBER
        #LINE 2
        revolutionNumber = 4801 # ARBITRARY NUMBER

        ### OUTPUT THE TLE FILE

        # WRITE TLE LINE 1
        TLE_LINE1 = '1                                                                   '
        TLE_LINE1 = insertData(TLE_LINE1, str(satelliteCatalog),2)
        TLE_LINE1 = insertData(TLE_LINE1, classification, 7)
        TLE_LINE1 = insertData(TLE_LINE1, str(intDesignatorYear), 9)
        TLE_LINE1 = insertData(TLE_LINE1, intDesignatorPiece,14)
        TLE_LINE1 = insertData(TLE_LINE1, str(epoch), 18)
        if str(derivative)[0] == '-':
            TLE_LINE1 = insertData(TLE_LINE1, str(derivative), 33)
        else:
            TLE_LINE1 = insertData(TLE_LINE1, str(derivative), 34)  
        TLE_LINE1 = insertData(TLE_LINE1, secondDerivative, 45)
        if str(drag)[0] == '-':
            TLE_LINE1 = insertData(TLE_LINE1, str(drag), 53)
        else:
            TLE_LINE1 = insertData(TLE_LINE1, str(drag), 54)  
        TLE_LINE1 = insertData(TLE_LINE1, str(ephemeris), 62)
        TLE_LINE1 = insertData(TLE_LINE1, str(elementSetNumber), 65)
        TLE_LINE1 = insertData(TLE_LINE1, str(checkSum(TLE_LINE1)), 68)
        #print(TLE_LINE1)

        # WRITE TLE LINE 2
        TLE_LINE2 = '2                                                                   '
        TLE_LINE2 = insertData(TLE_LINE2, str(satelliteCatalog), 2)
        TLE_LINE2 = insertData(TLE_LINE2, str(inclination), 8 + 3 - len(inclination.split(".")[0])) # ADDED SUPPORT FOR INCLINATIONS WITH 1-3 DIGIT INTEGER INCLINATIONS
        TLE_LINE2 = insertData(TLE_LINE2, str(raan), 17 + 3 - len(raan.split(".")[0])) # ADDED SUPPORT FOR RAANS WITH 1-3 DIGIT INTEGER RAANS
        TLE_LINE2 = insertData(TLE_LINE2, str(eccentricity)[2:]	, 26)
        TLE_LINE2 = insertData(TLE_LINE2, str(argPerigee), 34 + 3 - len(argPerigee.split(".")[0])) # ADDED SUPPORT FOR ARGUMENTS OF PERIGEE WITH 1-3 DIGIT INTEGER ARGUMENTS OF PERIGEE
        TLE_LINE2 = insertData(TLE_LINE2, str(meanAnomaly), 43 + 3 - len(meanAnomaly.split(".")[0])) # ADDED SUPPORT FOR MEAN ANOMALIES WITH 1-3 DIGIT INTEGER MEAN ANOMALIES
        TLE_LINE2 = insertData(TLE_LINE2, str(meanMotion), 52 + 2 - len(str(meanMotion).split(".")[0])) # ADDED SUPPORT FOR MEAN MOTIONS WITH 1-3 DIGIT INTEGER MEAN MOTIONS 
        TLE_LINE2 = insertData(TLE_LINE2, str(revolutionNumber), 64)
        TLE_LINE2 = insertData(TLE_LINE2, str(checkSum(TLE_LINE2)), 68)
        #print(TLE_LINE2)

        # CREATE TLE FILE 
        outputTLE = satelliteName + '\n' + TLE_LINE1.rstrip() + '\n' + TLE_LINE2.rstrip()
        print(outputTLE)

        with open('diwataTLE.txt', 'w') as file:
            file.write(outputTLE)
            file.close()
        
        # UPDATE THE GUI WITH THE RECEIVED TLE
        gui.tleCount = gui.tleCount + 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        gui.update_tle(timestamp, outputTLE)

#########################################################################################################

# CREATE A GUI THAT WILL PRINT RECEIVED TLE DATA
class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TLE Receiver Software")
        self.root.geometry("700x250")

        # LABEL FOR RECEIVED TLE
        self.tle_label = mtk.Label(root, text="Waiting for TLE", font= ("Arial", 14))
        self.tle_label.pack()

        # COUNT NUMBER OF TLEs RECEIVED
        self.tleCount = 0

    # FUNCTION TO UPDATE THE TEXT ON THE GUI WITH THE RECEIVED TLE
    def update_tle(self, timestamp, outputTLE):
        output = "Received TLE!\n\n Timestamp: " + timestamp + '\n\n# of TLE Received: ' + str(self.tleCount) + '\n\n' + outputTLE
        self.tle_label.configure(text=output)



# MAIN LOOP OF THE TLE RECEIVER SOFTWARE
if __name__ == "__main__":
    root = tk.Tk()
    gui = GUI(root)

    t1 = threading.Thread(target=receiveTLE, args=(gui,), daemon=True)
    t1.start()

    root.mainloop()


# run "pyinstaller --onefile groundStationSW.py" to create .exe file
