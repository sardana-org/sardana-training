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
from sardana.pool.controller import CounterTimerController


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
    def __init__(self, inst, props, *args, **kwargs):
        CounterTimerController.__init__(self,inst,props, *args, **kwargs)

    def LoadOne(self, axis, value):
        pass

    def StateOne(self, axis):
        # due to sardana-org/sardana #621 we need to return also status
        pass

    def StartOne(self, axis, _):
        pass

    # due to sardana-org/sardana #622 we need to implement StartAll
    def StartAll(self):
        pass

    def ReadOne(self, axis):
        pass

    def AbortOne(self, axis):
        pass
