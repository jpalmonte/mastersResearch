//fil.cpp - Filter library.
//Copyright (c) 2015-2018 Julie VK3FOWL and Joe VK3YSP
//For more information please visit http://www.sarcnet.org
//Released under the GNU General Public License.
//Provides low pass filters for the sensors and motors 

#include "fil.h"

//Public methods

Fil::Fil(float Alpha) {
  //Constructor
  alpha = Alpha;
  last = 0;
}

float Fil::lpf(float Value) {
  //Low pass filter - Decrease alpha to increase damping factor
  float result = (alpha * Value) + last * (1 - alpha);
  last = result;
  return result;
}
