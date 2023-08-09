//mot.cpp - Motor library.
//Copyright (c) 2015-2018 Julie VK3FOWL and Joe VK3YSP
//For more information please visit http://www.sarcnet.org
//Released under the GNU General Public License.
//Provides DC motor speed and direction control

#include "mot.h"

//Public methods

Mot::Mot(int type, float alpha, int gain, int pin1, int pin2): fil(alpha) {
  //Constructor
  _type = type;
  _gain = gain;
  _pin1 = pin1;
  _pin2 = pin2;
  pinMode(_pin1, OUTPUT);
  pinMode(_pin2, OUTPUT);
}

void Mot::halt() {
  drive(0.0);
}

void Mot::drive(float err) {
  switch (_type) {
    case PWMDIR:
      _pwmdir(err);
      break;
    case FWDREV:
      _fwdrev(err);
      break;
    case ACMOTR:
      _acmotr(err);
      break;
  }
}

void Mot::_fwdrev(float err) {
  //Drive the motors to reduce the antenna pointing errors to zero
  //Calculate the motor speed: A linear ramp close to zero; constant full speed beyond that.
  float spd = constrain(err * _gain, -255, 255);
  //Low pass filter the speed to reduce abrubt changes in speed
  spd = fil.lpf(spd);
  //For L298N DC Motor H-Bridge Driver Boards
  //Set the motor speed
  if (abs(err) < 0.5) {
    analogWrite(_pin1, 0);
    analogWrite(_pin2, 0);
  } else {
    if (spd > 0) {
      analogWrite(_pin1, (byte)(spd));
      analogWrite(_pin2, 0);
    } else {
      analogWrite(_pin1, 0);
      analogWrite(_pin2, (byte)(-spd));
    }
  }
}

void Mot::_pwmdir(float err) {
  //Drive the motors to reduce the antenna pointing errors to zero
  //Calculate the motor speed: A linear ramp close to zero; constant full speed beyond that.
  float spd = constrain(err * _gain, -255, 255);
  //Low pass filter the speed to reduce abrubt changes in speed
  spd = fil.lpf(spd);
  //For LMD18200T DC Motor H-Bridge Driver Boards
  //Set the motor speed
  if (abs(err) < 0.5) {
    analogWrite(_pin1, 0);                //Disengage motor drive when the error is small to reduce dither, noise and current consumption
  } else {
    analogWrite(_pin1, (byte)(abs(spd))); //Drive the motor
  }
  //Set the motor direction
  digitalWrite(_pin2, (spd > 0) ? HIGH : LOW);
}

void Mot::_acmotr(float err) {
  //AC Motor Driver
  //Reduce the antenna pointing error in degrees (err) to the minimum error (minErr)
  //by driving the motor at full speed until the maximum error (maxErr) point is reached.
  //Then start PWM by pulsing the motor on and off for the on time (onTime)
  //followed by the off time (offTime) until the maximum off time (maxOffTime) is reached.
  //Stop driving the motor when the antenna pointing error is less than the minimum error.

  //Constants
  const int onTime = 20;        //Set the on pulse time in milliseconds
  const int minErr = 1;         //Set the minimum error to start driving
  const int maxOffTime = 100;   //Set the maximum off time in milliseconds
  const int maxErr = 20;         //Set the maximum error to engage full speed

  //Variables
  unsigned long offTime;

  //Low pass filter the error to reduce abrubt changes in speed
  err = fil.lpf(err);

  float absErr = abs(err);  //Get the absolute magnitude of the error

  if (absErr >= minErr) { //Check if the error is above the minimum
    //If it is prepare to generate the PWM signals
    if (absErr > maxErr) { //Check if the error is above the maximum
      offTime = 0;  //If it is prepare to drive the motor at full speed
    } else {
      offTime = float(maxOffTime) * (float(maxErr) - absErr) / float(maxErr);   //Compute the off time in milliseconds
    }
    unsigned long thisTime = millis();  //Get the current time in milliseconds
    if (thisTime > (lastTime + onTime)) {
      //The drive pulse has completed, so set all the drive outputs low.
      digitalWrite(_pin1, LOW);
      digitalWrite(_pin2, LOW);
    }
    if (thisTime > (lastTime + onTime + offTime)) {
      //The PWM cycle is now complete. Start another drive pulse.
      if (err <= 0) {
        digitalWrite(_pin2, HIGH); //If the error is negative drive the CW pin
      } else {
        digitalWrite(_pin1, HIGH); //If the error is positive drive the CCW pin
      }
      lastTime = thisTime;         //Reset the stopwatch
    }
  } else {
    //The minimum error has been reached so stop the drive
    digitalWrite(_pin1, LOW);
    digitalWrite(_pin2, LOW);
  }
}
