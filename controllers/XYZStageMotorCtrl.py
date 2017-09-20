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
from sardana.sardanadefs import State
from sardana.pool.controller import MotorController, Type, Description,\
    DefaultValue


class CommunicationError(Exception):
    pass


class XYZStage(object):

    ACQ = 0
    CMD = 1
    ANS = 2

    AXES = "xyz"
    STATE_MAP = {"ON": State.On, "MOVING": State.Moving}

    def __init__(self, host, port):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))

    def __del__(self):
        self._socket.close()

    def ask(self, command):
        try:
            self._socket.sendall(command)
            data = self._socket.recv(4096)
        except:
            raise CommunicationError("send/recv failed")
        data = data.split(":")
        if (len(data) < 3 or
            data[self.ACQ] != "OK" or
            data[self.CMD] != command):
            raise CommunicationError("unrecognized response")
        return data[self.ANS]


class XYZStageMotorController(MotorController):
    """This class is the Sardana motor controller for the XYZ stage."""

    MaxDevice = 3

    ctrl_properties = \
        {'Host': {Type : str,
                  Description : 'Host where runs the XYZ stage server' },
         'Port': {Type : int,
                  Description : 'Port on which listens the XYZ stage server',
                  DefaultValue : 5000},
        }

    axis_attributes = \
    {
        "Label": {Type : str,
                  Description : 'The name of axis label' }
    }

    ctrl_attributes = \
    {
        "Color": {Type : str,
                  Description : 'The color of plot line' }
    }

    def __init__(self, inst, props, *args, **kwargs):
        MotorController.__init__(self, inst, props, *args, **kwargs)
        self.xyz_stage = XYZStage(self.Host, self.Port)
        self._states = {}
        self._raw_states = [None] * 3

    def __del__(self):
        del self.xyz_stage

    def getLabel(self):
        return self.Label

    def setLabel(self, axis, value):

        idx = axis - 1
        axis_name = XYZStage.AXES[idx]
        self.xyz_stage.ask("label %s %s" % (axis_name, value))
        self.Label = value

    def getColor(self):
        return self.Color

    def setColor(self, value):

        self.xyz_stage.ask("color %s" % value)
        self.Color = value

    def PreStateAll(self):
        self._raw_states = [None] * 3

    def StateAll(self):
        data = self.xyz_stage.ask("states")
        self._raw_states = data.split()

    def StateOne(self, axis):
        idx = axis - 1
        raw_state = self._raw_states[idx]
        limit_switches = 0
        state = XYZStage.STATE_MAP.get(raw_state, State.Unknown)
        return state, limit_switches

    def PreReadAll(self):
        self._raw_positions = [float("NaN")] * 3

    def ReadAll(self):
        data = self.xyz_stage.ask("positions")
        self._raw_positions = data.split()

    def ReadOne(self, axis):
        idx = axis - 1
        raw_position = self._raw_positions[idx]
        position = float(raw_position)
        return position

    def PreStartOne(self, axis, pos):
        return True

    def StartOne(self, axis, pos):
        idx = axis - 1
        axis_name = XYZStage.AXES[idx]
        self.xyz_stage.ask("move %s %f" % (axis_name, pos))

    def AbortOne(self, axis):
        self.xyz_stage.ask("abort")

    def SendToCtrl(self, cmd):
        return self.xyz_stage.ask(cmd)
