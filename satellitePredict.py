'''from pyorbital.orbital import Orbital
import numpy as np
import time
from datetime import datetime
import os

timestamp = datetime.now()

tle = os.getcwd() + '\dist\DIWATA-2B.txt'
latitude = 33.8924
longitude = 130.8403

satellite = Orbital('DIWATA-2B',tle_file=tle)
nextPasses = satellite.get_next_passes(timestamp,7,longitude,latitude,alt = 50, tol = 1e-3, horizon = 0)

print(timestamp)
for rise_time, fall_time, max_elev_time in nextPasses:
    print(rise_time)
    print(fall_time)
    print(max_elev_time)
'''
    
import win32gui
import re


class WindowMgr:
    """Encapsulates some calls to the winapi for window management"""

    def __init__ (self):
        """Constructor"""
        self._handle = None

    def find_window(self, class_name, window_name=None):
        """find a window by its class_name"""
        self._handle = win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        """Pass to win32gui.EnumWindows() to check all the opened windows"""
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
            self._handle = hwnd

    def find_window_wildcard(self, wildcard):
        """find a window whose title matches the wildcard regex"""
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        """put the window in the foreground"""
        win32gui.SetForegroundWindow(self._handle)


w = WindowMgr()
w.find_window_wildcard(".*Hello.*")
w.set_foreground()