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

from sardana import State
from sardana.pool.controller import MotorController, Type, Description,\
    DefaultValue


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

    ctrl_properties = \
        {"Host": {Type : str,
                  Description : "Host where runs the blander blades server",
                  DefaultValue : "localhost"},
         "Port": {Type : int,
                  Description : "Port the blender blades server listens on",
                  DefaultValue : 9999},
        }

    # sardana motor axis to blender blades axis name map
    AXIS_NAMES = {1: "top", 2: "bot", 3: "left", 4: "right"}
    # blender blades axis state to sardana motor state map
    STATES = {"ON": State.On, "MOVING": State.Moving}
    # parameter name position in blender blades answer
    PARAM = 0
    # parameter value position in blender blades answer
    VALUE = 1

    def __init__(self, inst, props, *args, **kwargs):
        super_class = super(BlenderBladesMotorController, self)
        super_class.__init__(inst, props, *args, **kwargs)
        host = self.Host
        port = self.Port
        self.blender_blades = BlenderBlades(host, port)

    def __del__(self):
        del self.blender_blades

    def StateOne(self, axis):
        axis_name = self.AXIS_NAMES[axis]
        blender_blades = self.blender_blades
        ans = blender_blades.ask("?state {0}".format(axis_name))
        state_raw = ans.split()[self.VALUE]
        state = self.STATES[state_raw]
        limit_switches = MotorController.NoLimitSwitch
        return state, limit_switches

    def ReadOne(self, axis):
        axis_name = self.AXIS_NAMES[axis]
        blender_blades = self.blender_blades
        ans = blender_blades.ask("?pos {0}".format(axis_name))
        position_raw = ans.split()[self.VALUE]
        position = float(position_raw)
        return position

    def StartOne(self, axis, position):
        axis_name = self.AXIS_NAMES[axis]
        blender_blades = self.blender_blades
        ans = blender_blades.ask("move {0} {1}".format(axis_name, position))

    def AbortOne(self, axis):
        blender_blades = self.blender_blades
        blender_blades.ask("abort")

    def GetAxisPar(self, axis, name):
        axis_name = self.AXIS_NAMES[axis]
        blender_blades = self.blender_blades
        name = name.lower()
        if name == "acceleration":
            ans = blender_blades.ask("?acc {0}".format(axis_name))
            acc_raw = ans.split()[self.VALUE]
            v = float(acc_raw)
        elif name == "deceleration":
            ans = blender_blades.ask("?dec {0}".format(axis_name))
            dec_raw = ans.split()[self.VALUE]
            v = float(dec_raw)
        elif name == "base_rate":
            v = 0
        elif name == "velocity":
            ans = blender_blades.ask("?vel {0}".format(axis_name))
            vel_raw = ans.split()[self.VALUE]
            v = float(vel_raw)
        elif name == "step_per_unit":
            v = 1
        return v

    def SetAxisPar(self, axis, name, value):
        axis_name = self.AXIS_NAMES[axis]
        blender_blades = self.blender_blades
        name = name.lower()
        if name == "acceleration":
            blender_blades.ask("acc {0} {1}".format(axis_name, value))
        elif name == "deceleration":
            blender_blades.ask("dec {0} {1}".format(axis_name, value))
        elif name == "base_rate":
            raise Exception("base_rate is always 0")
        elif name == "velocity":
            blender_blades.ask("vel {0} {1}".format(axis_name, value))
        elif name == "step_per_unit":
            raise Exception("step_per_unit is always 1")

