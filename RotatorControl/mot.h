//mot.h - Motor library.
//Copyright (c) 2015-2018 Julie VK3FOWL and Joe VK3YSP
//For more information please visit http://www.sarcnet.org
//Released under the GNU General Public License.
//Provides DC motor speed and direction control

#ifndef MOT_H
#define MOT_H

#include "fil.h"
#include <Arduino.h>

//Motor type definitions
#define PWMDIR 0 //For single PWM output with direction and break control. E.g. LMD18200T
#define FWDREV 1 //For dual forward and reverse PWM output with no direction and break control. E.g. L298N
#define ACMOTR 2 //For AC Motor driver E.g. APTINEX 4 Channel Triac Module MOC3061 BT139 600V 16A

class Mot {
  public:
    Mot(int type, float alpha, int gain, int pin1, int pin2);
    void halt();
    void drive(float err);
  private:
    int _type, _gain, _pin1, _pin2;
    unsigned long lastTime;
    void _pwmdir(float err);
    void _fwdrev(float err);
    void _acmotr(float err);
    Fil fil;
};
#endif
