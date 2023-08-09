//timer.h - Timer library.
//Copyright (c) 2015-2018 Julie VK3FOWL and Joe VK3YSP
//For more information please visit http://www.sarcnet.org
//Released under the GNU General Public License.
//Provides a non-blocking millisecond timer object that can be used to replace the delay() function

#ifndef TIMER_H
#define TIMER_H

#include <Arduino.h>

class Timer {
  public:
    Timer();                  //Use this constructor if you don't need to set a period
    Timer(long period);       //Use this constructor if you need to set a period
    void reset();             //Resets the start time to the current time since power up
    void reset(long period);  //Resets, as above, and sets the period
    bool timeout();           //Returns true if the period has elapsed
    long elapsed();           //Returns the number of milliseconds since reset 
    long periods();           //Returns the number of periods since reset
    bool toggle();            //Returns a value that toggles every period
    bool tick();              //Returns true if the period has elapsed since the last call
    void execute(void (*f)());//Executes function f once every period
  private:
    long _period;             //Period in milliseconds
    long _start;              //Start time in milliseconds since power up
    long _last;               //Last value of periods
};
#endif
