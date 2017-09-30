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


import time
import os
from sardana import State
from sardana.pool.controller import CounterTimerController


class MiniNetworkPackagesCounterTimerController(CounterTimerController):
    """ This controller provides interface for network packages counting."""

    MaxDevice = 1

    def __init__(self, inst, props, *args, **kwargs):
        CounterTimerController.__init__(self,inst,props, *args, **kwargs)
        self.acq_time = 1.
        self.acq_end_time = time.time()
        self.start_counts = 0

    def AddDevice(self, axis):
        pass

    def DeleteDevice(self, axis):
        pass

    def LoadOne(self, axis, value):
        self.acq_time = value

    def StateOne(self, axis):
        state = State.On
        if time.time() < self.acq_end_time:
            state = State.Moving
        status_string = 'My custom status info'
        return state, status_string

    def StartOne(self, axis, value):
        self._log.debug("StartOne receives %f" % value)
        self.acq_end_time = time.time() + self.acq_time
        self.start_counts = self.read_network_counts()

    def ReadOne(self, axis):
        counts = self.read_network_counts()
        return counts - self.start_counts

    def StartAll(self):
        pass

    def AbortOne(self, axis):
        self.acq_end_time = time.time()

    def read_network_counts(self):
        with os.popen('cat /proc/net/dev |grep eno1') as fd:
            output = fd.read()
            recv_bytes_start = output.find(':') + 2
            recv_bytes_end = output.find(' ', recv_bytes_start)
            return int(output[recv_bytes_start:recv_bytes_end])
