//lsm.cpp - Library for LSM303 Accelerometer/Magnetometer.
//Copyright (c) 2015-2018 Julie VK3FOWL and Joe VK3YSP
//Released under the GNU General Public License.
//For more information please visit http://www.sarcnet.org
//Submitted for publication in Amateur Radio magazine: December 2015
//First published in Amateur Radio magazine: May 2016
//Upgraded Mk2 version published in Amateur Radio magazine: October 2016
//Reference: ST Datasheet: LSM303 Ultra-compact high-performance eCompass module: 3D accelerometer and 3D magnetometer
//There are two types of supported sensor boards containing the LSM303D or LSL303DHLC integrated circuits.
//Because the flat side of the sensor board is attached on the top of the antenna boom, with the long side of the sensor board parallel to the boom,
//the sensor axes (X', Y' and Z') are not the same as the reference axes (X, Y and Z) used in the software and our original article.
//X = -Y', Y = X' and Z = Z'. Also, the gravity field vector G is the opposite of the device acceleration vector A.
//Therefore the following transformations apply: MX = -MY', MY = MX', MZ = MZ', GX = AY', GY = -AX', GZ = -AZ'.
//Supports LSM303D or LSM303DLHC 3D Accelerometer/Magnetometer

#include "lsm.h"

//Public methods

Lsm::Lsm(int type, float alpha): filMX(alpha), filMY(alpha), filMZ(alpha), filGX(alpha), filGY(alpha), filGZ(alpha) {
  //Constructor
  //Note: Wire.h cannot be initialized from a class constructor - see begin() method
  _type = type;
}

void Lsm::begin() {
  //Reset the sensor
  reset();
  //Initialize the sensor filters
  for (int i = 0; i < 50; i++) readGM();
}

void Lsm::reset() {
  //Reset the sensor
  Wire.begin();                                         //Initialize the I2C bus
  switch (_type) {
    case LSM303D:
      writeReg(LSM303D_ADDRESS, LSM303D_CTRL1, 0b01010111); //Acc output data rate = 50Hz all Acc axes enabled.
      writeReg(LSM303D_ADDRESS, LSM303D_CTRL2, 0b00000000); //Acc full scale = +/- 2g
      writeReg(LSM303D_ADDRESS, LSM303D_CTRL5, 0b01100100); //Mag output data rate = 6.25HzMag resolution = high;
      writeReg(LSM303D_ADDRESS, LSM303D_CTRL6, 0b00100000); //Mag full scale = +/- 4gauss
      writeReg(LSM303D_ADDRESS, LSM303D_CTRL7, 0b00000000); //Mag low power mode = Off. Mag sensor mode = Continuous-conversion
      break;
    case LSM303DLHC:
      writeReg(LSM303DLHC_ADDRESS_A, LSM303DLHC_CTRL_REG1_A, 0b01000111); //Acc output data rate = 50Hz all Acc axes enabled.
      writeReg(LSM303DLHC_ADDRESS_A, LSM303DLHC_CTRL_REG4_A, 0b00001000); //Acc full scale = +/- 2g, High Resolution Enable
      writeReg(LSM303DLHC_ADDRESS_M, LSM303DLHC_CRA_REG_M, 0b00011000); //Mag output data rate = 30Hz
      writeReg(LSM303DLHC_ADDRESS_M, LSM303DLHC_CRB_REG_M, 0b00101000); //Mag full scale = +/- 1.3g
      writeReg(LSM303DLHC_ADDRESS_M, LSM303DLHC_MR_REG_M, 0b00000000); //Mag Continuous Conversion Mode
      break;
  }
}

void Lsm::calStart() {
  //Prepare to calibrate the sensor
  calMX.reset();
  calMY.reset();
  calMZ.reset();
  calGX.reset();
  calGY.reset();
  calGZ.reset();
}

void Lsm::readGM() {
  //Read the accelerometer and magnetometer
  reset();  //Reinitialise I2C and the sensor before each read as it is inclined to lock up after running a long time
  readG();
  readM();
}

bool Lsm::calibrate() {
  //Caculate the 3D scaling factors and errors for the magnetometer and accelerometer
  bool changed = false;
  //Update exisiting maximums and minimums based on current values
  changed = calMX.sample(mx, changed);
  changed = calMY.sample(my, changed);
  changed = calMZ.sample(mz, changed);
  changed = calGX.sample(gx, changed);
  changed = calGY.sample(gy, changed);
  changed = calGZ.sample(gz, changed);
  if (changed) {
    //Calculate the error vectors
    cal.me = Vec(calMX.offset, calMY.offset, calMZ.offset);
    cal.ge = Vec(calGX.offset, calGY.offset, calGZ.offset);
    //Caclulate the scaling vectors
    cal.ms = Vec(calMX.scale, calMY.scale, calMZ.scale);
    cal.gs = Vec(calGX.scale, calGY.scale, calGZ.scale);
  }
  return changed;
}

void Lsm::getAzEl() {
  //Get the antenna azimuth and elevation angles
  //Get the unit vectors for the earth's magnetic and gravitational fields
  //For each component subtract the error and divide by the scaling factor
  readGM();
  Vec M = Vec((mx - cal.me.i) / cal.ms.i, (my - cal.me.j) / cal.ms.j, (mz - cal.me.k) / cal.ms.k).unit();
  Vec G = Vec((gx - cal.ge.i) / cal.gs.i, (gy - cal.ge.j) / cal.gs.j, (gz - cal.ge.k) / cal.gs.k).unit();
  //Define the antenna axes as the main reference axes
  Vec X = Vec(1.0, 0.0, 0.0);         //The antenna X vector
  Vec Y = Vec(0.0, 1.0, 0.0);         //The antenna Y (boresight) vector
  Vec Z = Vec(0.0, 0.0, 1.0);         //The antenna Z vector
  //Compute the magnetic ground axes relative to the antenna axes
  Vec E = G.cross(M);                   //The magnetic East vector
  Vec N = E.cross(G);                   //The magnetic North vector
  Vec U = G.neg();                        //The magnetic Up vector
  //Compute the projections of the antenna axes onto the magnetic ground axes
  float Xn = X.dot(N);                     //The scalar projection of X onto N
  float Xe = X.dot(E);                     //The scalar projection of X onto E
  float Yu = Y.dot(U);                     //The scalar projection of Y onto U
  float Zu = Z.dot(U);                     //The scalar projection of Z onto U
  //Compute the true antenna pointing angles relative to the magnetic ground axes
  az = atan2(-Xn, Xe) * rad2deg + cal.md;  //The azimuth angle in degrees using the X-axis
  el = atan2(Yu, Zu) * rad2deg;            //The elevation angle in degrees using the Y-axis
  if (az > 180) az = az - 360;           //Ensure azimuth is in -180..180 format after adding D
}

//Private methods

void Lsm::readG() {
  switch (_type) {
    case LSM303D:
      //Read the 3D accelerometer to determine the gravitational field vector
      Wire.beginTransmission((byte)LSM303D_ADDRESS);
      Wire.write(LSM303D_OUT_X_L_A | 0x80);
      Wire.endTransmission();
      Wire.requestFrom((byte)LSM303D_ADDRESS, (byte)6);
      if (Wire.available() == 6) {
        //Read 8-bit values
        byte  xl = Wire.read();
        byte  xh = Wire.read();
        byte  yl = Wire.read();
        byte  yh = Wire.read();
        byte  zl = Wire.read();
        byte  zh = Wire.read();
        //Assemble 16-bit values and perform the axis transformation
        gx = ((yh << 8) | yl);
        gy = -((xh << 8) | xl);
        gz = -((zh << 8) | zl);
        //Low pass filter the sensor data as it improves the calibration procedure
        gx = filGX.lpf(gx);
        gy = filGY.lpf(gy);
        gz = filGZ.lpf(gz);
      }
      break;
    case LSM303DLHC:
      //Read the 3D accelerometer to determine the gravitational field vector
      Wire.beginTransmission((byte)LSM303DLHC_ADDRESS_A);
      Wire.write(LSM303DLHC_OUT_X_L_A | 0x80);
      Wire.endTransmission();
      Wire.requestFrom((byte)LSM303DLHC_ADDRESS_A, (byte)6);
      if (Wire.available() == 6) {
        //Read 8-bit values
        byte  xl = Wire.read();
        byte  xh = Wire.read();
        byte  yl = Wire.read();
        byte  yh = Wire.read();
        byte  zl = Wire.read();
        byte  zh = Wire.read();
        //Assemble 16-bit values and perform the axis transformation
        gx = ((yh << 8) | yl);
        gy = -((xh << 8) | xl);
        gz = -((zh << 8) | zl);
        //Low pass filter the sensor data as it improves the calibration procedure
        gx = filGX.lpf(gx);
        gy = filGY.lpf(gy);
        gz = filGZ.lpf(gz);
      }
      break;
  }
}

void Lsm::readM() {
  switch (_type) {
    case LSM303D:
      //Read the 3D magnetometer to determine the magnetic field vector
      Wire.beginTransmission((byte)LSM303D_ADDRESS);
      Wire.write(LSM303D_OUT_X_L_M | 0x80);
      Wire.endTransmission();
      Wire.requestFrom((byte)LSM303D_ADDRESS, (byte)6);
      if (Wire.available() == 6) {
        //Read 8-bit values
        byte xl = Wire.read();
        byte xh = Wire.read();
        byte yl = Wire.read();
        byte yh = Wire.read();
        byte zl = Wire.read();
        byte zh = Wire.read();
        //Assemble 16-bit values and perform the axis transformation
        mx = -((yh << 8) | yl);
        my = ((xh << 8) | xl);
        mz = ((zh << 8) | zl);
        //Low pass filter the sensor data as it improves the calibration procedure
        mx = filMX.lpf(mx);
        my = filMY.lpf(my);
        mz = filMZ.lpf(mz);
      }
      break;
    case LSM303DLHC:
      //Read the 3D magnetometer to determine the magnetic field vector
      Wire.beginTransmission((byte)LSM303DLHC_ADDRESS_M);
      Wire.write(LSM303DLHC_OUT_X_H_M | 0x80);
      Wire.endTransmission();
      Wire.requestFrom((byte)LSM303DLHC_ADDRESS_M, (byte)6);
      if (Wire.available() == 6) {
        //Read 8-bit values
        byte xh = Wire.read();
        byte xl = Wire.read();
        byte zh = Wire.read();
        byte zl = Wire.read();
        byte yh = Wire.read();
        byte yl = Wire.read();
        //Assemble 16-bit values and perform the axis transformation
        mx = -((yh << 8) | yl);
        my = ((xh << 8) | xl);
        mz = ((zh << 8) | zl);
        //Low pass filter the sensor data as it improves the calibration procedure
        mx = filMX.lpf(mx);
        my = filMY.lpf(my);
        mz = filMZ.lpf(mz);
      }
      break;
  }
}

void Lsm::writeReg(byte address, byte reg, byte value) {
  //I2C write to register at address
  Wire.beginTransmission(address);
  Wire.write(reg);
  Wire.write(value);
  Wire.endTransmission();
}

byte Lsm::readReg(byte address, byte reg) {
  //I2C read from register at address
  byte value;
  Wire.beginTransmission(address);
  Wire.write(reg);
  Wire.endTransmission();
  Wire.requestFrom(address, (byte)1);
  value = Wire.read();
  Wire.endTransmission();
  return value;
}
