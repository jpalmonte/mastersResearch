//timer.cpp - Timer library.
//Copyright (c) 2015-2018 Julie VK3FOWL and Joe VK3YSP
//For more information please visit http://www.sarcnet.org
//Released under the GNU General Public License.
//Provides a non-blocking millisecond timer object that can be used to replace the delay() function

#include "timer.h"

Timer::Timer() {
  //Use this constructor if you don't need to set a period
  reset();
}

Timer::Timer(long period) {
  //Use this constructor if you need to set a period
  _period = period;
  _last = 0;
  reset();
}

void Timer::reset() {
  //Resets the start time to the current time since power up
  _start = millis();
  _last = 0;
}

void Timer::reset(long period) {
  //Resets, as above and sets the period
  _period = period;
  reset();
}

bool Timer::timeout() {
  //Returns true if the period has elapsed
  return (elapsed() >= _period);
}

long Timer::elapsed() {
  //Returns the number of milliseconds since reset
  return millis() - _start;
}

long Timer::periods() {
  //Returns the number of periods since reset
  return long(elapsed() / _period);
}

bool Timer::toggle() {
  //Return value toggles every period
  return (periods() % 2); //Returns true for odd and false for even using the mod function
}

bool Timer::tick() {
  //Returns true if the period has elapsed since the last call
  long p = periods();
  if (p > _last) {
    _last = p;
    return true;
  } else {
    return false;
  }
}

void Timer::execute(void (*f)()){
  //Executes function f once every period
  if (tick()){
    (*f)();
  }
}
