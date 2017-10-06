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

from sardana import State
from sardana.macroserver.macro import macro, Type

# define macro parameters
@macro()
def oscillate(self):
    """Acquire with the active measurement group while oscillating a motor.
    """
    # reserve motion and measurement group objects
    # read current position and prepare positions array
    # put integration time to the measurement group
    # start count in the asynchronous way
    # wait for count
    # while measurement group is counting move oscillate the motor
    # increment counter and use modulo operation to alternate position
    pass
