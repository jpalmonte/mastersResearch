//cal.h - Calibration library.
//Copyright (c) 2015-2018 Julie VK3FOWL and Joe VK3YSP
//For more information please visit http://www.sarcnet.org
//Released under the GNU General Public License.
//Provides calibration objects for each axis
//The offset and scaling factors are accumulated by sampling data

#ifndef CAL_H
#define CAL_H

#include <Arduino.h>

class Cal {
  public:
    Cal();
    void reset();
    void compute();
    bool sample(int a, bool changed);
    int offset;
    int scale;
  private:
    int _min;
    int _max;
};
#endif
