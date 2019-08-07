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

import os
import time
from sardana import State
from sardana.pool.controller import CounterTimerController, Type,\
    Description, DefaultValue


def read_network_counts(interface):
    cmd = 'cat /proc/net/dev | grep {0}'.format(interface)
    with os.popen(cmd) as fd:
        output = fd.read()
        bytes_raw = output.split()[1]
        return int(bytes_raw)


class NetworkTrafficCounterTimerController(CounterTimerController):
    """This controller provides interface for network packages counting.
    It counts the number of bytes of data transmitted or received by a network
    interface over the integration time.
    """

    default_timer = 1

    ctrl_properties = {
        'interface': {Type: str,
                      Description: 'network interface to count packages',
                      DefaultValue: 'eno1'},
    }

    def __init__(self, inst, props, *args, **kwargs):
        CounterTimerController.__init__(self, inst, props, *args, **kwargs)
        self.acq_time = 1.
        self.acq_end_time = time.time()
        self.start_counts = 0

    def LoadOne(self, axis, value):
        self.acq_time = value

    def StateOne(self, axis):
        state = State.On
        if time.time() < self.acq_end_time:
            state = State.Moving
        # due to sardana-org/sardana #621 we need to return also status
        status_string = 'My custom status info'
        return state, status_string

    def StartOne(self, axis, _):
        self.acq_end_time = time.time() + self.acq_time
        self.start_counts = read_network_counts(self.interface)

    def ReadOne(self, axis):
        counts = read_network_counts(self.interface)
        return counts - self.start_counts

    def AbortOne(self, axis):
        self.acq_end_time = time.time()
