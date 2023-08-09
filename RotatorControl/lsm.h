//lsm.h - Library for LSM303 Accelerometer/Magnetometer.
//Copyright (c) 2015-2018 Julie VK3FOWL and Joe VK3YSP
//Released under the GNU General Public License.
//For more information please visit http://www.sarcnet.org
//Submitted for publication in Amateur Radio magazine: December 2015
//First published in Amateur Radio magazine: May 2016
//Upgraded MkII version published in Amateur Radio magazine: October 2016
//Reference: ST Datasheet: LSM303 Ultra-compact high-performance eCompass module: 3D accelerometer and 3D magnetometer
//There are two types of supported sensor boards containing the LSM303D or LSL303DHLC integrated circuits.
//Because the flat side of the sensor board is attached on the top of the antenna boom, with the long side of the sensor board parallel to the boom,
//the sensor axes (X', Y' and Z') are not the same as the reference axes (X, Y and Z) used in the software and our original article.
//X = -Y', Y = X' and Z = Z'. Also, the gravity field vector G is the opposite of the device acceleration vector A.
//Therefore the following transformations apply: MX = -MY', MY = MX', MZ = MZ', GX = AY', GY = -AX', GZ = -AZ'.
//Release 5
//Supports LSM303D or LSM303DLHC 3D Accelerometer/Magnetometer

#ifndef LSM_H
#define LSM_H

#include <Arduino.h>
#include <Wire.h>
#include "cal.h"
#include "fil.h"
#include "vec.h"

//Sensor type definitions
#define LSM303D 0     //For LSM303D sensor
#define LSM303DLHC 1  //For LSM303DLHC sensor

//LSM303D Registers
#define LSM303D_ADDRESS 0b0011101
#define LSM303D_OUT_X_L_A 0x28
#define LSM303D_OUT_X_L_M 0x08
#define LSM303D_CTRL1 0x20
#define LSM303D_CTRL2 0x21
#define LSM303D_CTRL3 0x22
#define LSM303D_CTRL4 0x23
#define LSM303D_CTRL5 0x24
#define LSM303D_CTRL6 0x25
#define LSM303D_CTRL7 0x26
//LSM303DLHC Registers
#define LSM303DLHC_ADDRESS_A 0b0011001
#define LSM303DLHC_ADDRESS_M 0b0011110
#define LSM303DLHC_OUT_X_L_A 0x28
#define LSM303DLHC_OUT_X_H_M 0x03
#define LSM303DLHC_CTRL_REG1_A 0x20
#define LSM303DLHC_CTRL_REG4_A 0x23
#define LSM303DLHC_CRA_REG_M 0x00
#define LSM303DLHC_CRB_REG_M 0x01
#define LSM303DLHC_MR_REG_M 0x02
class Lsm {
  public:
    Lsm(int type, float alpha);
    void begin();
    bool calibrate();
    void readGM();
    void getAzEl();
    //Uncalibrated magnetometer and accelerometer values
    int  mx, my, mz, gx, gy, gz;
    //Calibration data structure
    struct {
      float md;               //The magnetic declination
      Vec me, ge, ms, gs;  //Calibration vectors
    } cal;
    const float rad2deg = 57.295779513;   //Degrees per radian
    void reset();
    void calStart();
    float az, el;
  private:
    int _type;
    void readG();
    void readM();
    void writeReg(byte address, byte reg, byte value);
    byte readReg(byte address, byte reg);
    //Create calibration objects for each axis
    Cal calMX, calMY, calMZ, calGX, calGY, calGZ;
    //Create filter objects for each axis
    Fil filMX, filMY, filMZ, filGX, filGY, filGZ;
};
#endif
