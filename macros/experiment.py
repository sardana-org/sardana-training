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


@macro([["motor", Type.Motor, None, "Motor to oscilate"],
        ["amplitude", Type.Float, None, "Oscilation amplitude"],
        ["integ_time", Type.Float, None, "Integration time"]])
def oscilate(self, motor, amplitude, integ_time):
    """Acquire the active measurement group while oscilating a motor.
    """
    motion = self.getMotion([motor])
    curr_pos = motor.getPosition()
    positions = [curr_pos + amplitude / 2,
                 curr_pos - amplitude / 2]

    mnt_grp_name = self.getEnv("ActiveMntGrp")
    mnt_grp = self.getMeasurementGroup(mnt_grp_name)
    mnt_grp.putIntegrationTime(integ_time)

    i = 0
    id_ = mnt_grp.startCount()
    while mnt_grp.State() == State.Moving:
        self.checkPoint()  # place a check point so the loop can be aboerted
        motion.move(positions[i])
        i += 1
        i %= 2
    mnt_grp.waitCount(id_)
