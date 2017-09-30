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

from sardana.pool.controller import PseudoMotorController


class BlenderSlit(PseudoMotorController):
    """A Slit pseudo motor controller for handling gap and offset pseudo
    motors. The system uses the real motors top and bottom
    """

    pseudo_motor_roles = "gap", "offset"
    motor_roles = "top", "bottom"

    GAP = 1
    OFFSET = 2
    TOP = 1
    BOTTOM = 2

    def __init__(self, inst, props, *args, **kwargs):
        PseudoMotorController.__init__(self, inst, props, *args, **kwargs)

    def CalcPhysical(self, axis, pseudo_pos, curr_physical_pos):
        half_gap = pseudo_pos[self.GAP - 1] / 2.0
        if axis == self.TOP:
            ret = pseudo_pos[self.OFFSET - 1] + half_gap
        elif axis == self.BOTTOM:
            ret = half_gap - pseudo_pos[self.OFFSET - 1]
        return ret

    def CalcPseudo(self, axis, physical_pos, curr_pseudo_pos):
        gap = physical_pos[self.BOTTOM - 1] + physical_pos[self.TOP - 1]
        if axis == self.GAP:
            ret = gap
        elif axis == self.OFFSET:
            half_gap = gap / 2.0
            ret = physical_pos[self.TOP - 1] - half_gap
        return ret
