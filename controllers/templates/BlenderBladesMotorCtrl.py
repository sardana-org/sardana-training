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

import socket

from sardana.pool.controller import MotorController


class CommunicationError(Exception):
    pass


class BlenderBlades(object):

    CMD = 0
    ANS_START = 1

    def __init__(self, host, port):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))

    def __del__(self):
        self._socket.close()

    def ask(self, command):
        command = "{0}\n".format(command)
        try:
            self._socket.sendall(command)
            raw_data = self._socket.recv(4096)
        except:
            raise CommunicationError("send/recv failed")
        data = raw_data.split()
        ans = " ".join(data[self.ANS_START:])
        return ans


class BlenderBladesMotorController(MotorController):
    """A motor controller that inverfaces slit system composed from horizontal
    (left and right) and vertical (bottom and top) blades.

    The slit system must be rendered with blender player prior to the init of
    the controller: blenderplayer sardana-training/blender_slits/slits.blend.
    """
        # sardana motor axis to blender blades axis name map
    AXIS_NAMES = {1: "top", 2: "bot", 3: "left", 4: "right"}
    # blender blades axis state to sardana motor state map
    STATES = {"ON": State.On, "MOVING": State.Moving}
    # parameter name position in blender blades answer
    AXIS_ID = 0
    # parameter value position in blender blades answer
    VALUE = 1

    def __init__(self, inst, props, *args, **kwargs):
        super_class = super(BlenderBladesMotorController, self)
        super_class.__init__(inst, props, *args, **kwargs)

    def __del__(self):
        del self.blender_blades

    def StateOne(self, axis):
        axis_name = self.AXIS_NAMES[axis]
        limit_switches = MotorController.NoLimitSwitch  # no limits are active
        blender_blades = self.blender_blades

    def ReadOne(self, axis):
        axis_name = self.AXIS_NAMES[axis]
        blender_blades = self.blender_blades

    def StartOne(self, axis, position):
        axis_name = self.AXIS_NAMES[axis]
        blender_blades = self.blender_blades

    def AbortOne(self, axis):
        blender_blades = self.blender_blades
