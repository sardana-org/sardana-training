"""
This file is part of Sardana-Training documentation 
2017 ALBA Synchrotron
Sardana-Training documentation is free software: you can redistribute it and/or 
modify it under the terms of the GNU Lesser General Public License as published 
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
Sardana-Training documentation is distributed in the hope that it will be 
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License
along with Sardana-Training.  If not, see <http://www.gnu.org/licenses/>.
"""

# uses the package python-xlib
# from http://snipplr.com/view/19188/mouseposition-on-linux-via-xlib/
# or: sudo apt-get install python-xlib
from Xlib import display


class Mouse(object):

    def __init__(self):
        self.display = display.Display()
        self.mousepos()

    def get_xpos(self):
        self.mousepos()
        return self._X_POS

    def get_ypos(self):
        self.mousepos()
        return self._Y_POS
    
    def set_ypos(self, value):
        root = self.display.screen().root
        root.warp_pointer(self._X_POS, value)
        self.display.sync()

    def set_xpos(self, value):
        root = self.display.screen().root
        root.warp_pointer(value, self._Y_POS)
        self.display.sync()

    def mousepos(self):
        """mousepos() --> (x, y) get the mouse coordinates on the screen (linux, Xlib)."""
        data = self.display.screen().root.query_pointer()._data
        self._X_POS = data["root_x"]
        self._Y_POS = data["root_y"]
        self._Y_ROOT = data["root_x"]
        
    X_POS = property(get_xpos, set_xpos)
    Y_POS = property(get_ypos, set_ypos)



