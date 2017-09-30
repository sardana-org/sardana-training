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
        recv_bytes_start = output.find(':') + 2
        recv_bytes_end = output.find(' ', recv_bytes_start)
        return int(output[recv_bytes_start:recv_bytes_end])


class NetworkTrafficCounterTimerController(CounterTimerController):
    """This controller provides interface for network packages counting.
    It counts the number of bytes of data transmitted or received by a network
    interface over the integration time.
    """
    pass
