//fil.h - Filter library.
//Copyright (c) 2015-2018 Julie VK3FOWL and Joe VK3YSP
//For more information please visit http://www.sarcnet.org
//Released under the GNU General Public License.
//Provides low pass filters for the sensors and motors 

#ifndef FIL_H
#define FIL_H

#include <Arduino.h>

class Fil {
  public:
    Fil(float Alpha);
    float lpf(float Value);
  private:
    float last;
    float alpha;
};

#endif
