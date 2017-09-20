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


from math import tan, atan2

from sardana.pool.controller import Type, Description, PseudoMotorController


class MirrorVerticalPseudoMotorController(PseudoMotorController):
    """The PseudoMotor controller for the mirror table vertical pseudo
    motors. It provide z-translation and pitch and roll angles based on
    physical translations mzc, mzl and mzr.

    The user units must be mm for translations and mrad for angles.

    The pitch rotational axis is in the middle of y-dimension.
    The roll rotational axis is in the middle of x-dimension.
       ____________________________
      |                           |
      |                   *mzr    |
      |   *mzc                    |   <-------- beam direction
      |                   *mzl    |
      |___________________________|

    For example of mirror with dim_x = 261 mm and dim_y = 1262.5 increasing the
    pitch angle of 1 mrad should increase the mzc of 0.63125021041675084 mm and
    decrease the mzl and the mzr of 0.63125021041675084 mm.
    And increasing the roll angle of 1 mrad should increase the mzl
    of 0.13050004350001742 mm and decrease the mzr of 0.13050004350001742 mm.
    """

    pseudo_motor_roles = ('z', 'pitch', 'roll')
    motor_roles = ('mzc', 'mzl', 'mzr')

    Z = 1
    PIT = 2
    ROL = 3

    MZC = 1
    MZL = 2
    MZR = 3

    ctrl_properties = \
        {'dim_x': {Type : float,
                   Description : 'distance between mzr and mzl'},
         'dim_y': {Type : float,
                   Description : 'distance between mzc and mzr-mzl axis' }}

    def __init__(self, inst, props, *args, **kwargs):
        PseudoMotorController.__init__(self, inst, props, *args, **kwargs)
        self.dim_x = self.dim_x / 1000.  # change unit mm -> m
        self.dim_y = self.dim_y / 1000.  # change unit mm -> m

    def CalcPhysical(self, axis, pseudos, curr_physicals):
        z = pseudos[self.Z - 1]
        z = z / 1000.0  # change unit: mm -> m
        pit = pseudos[self.PIT - 1]
        pit = pit / 1000.0  # change unit: mrad -> rad
        if axis == self.MZC:
            m = z + tan(pit) * self.dim_y / 2
        elif axis == self.MZL or axis == self.MZR:
            rol = pseudos[self.ROL - 1]
            rol = rol / 1000.0  # change unit: mrad -> rad
            if axis == self.MZL:
                m = z - tan(pit) * self.dim_y / 2 + tan(rol) * self.dim_x / 2
            else:
                m = z - tan(pit) * self.dim_y / 2 - tan(rol) * self.dim_x / 2
        m = m * 1000  # change unit: m -> mm
        return m

    def CalcPseudo(self, axis, physicals, curr_pseudos):
        # Don't do that!
        return self.CalcAllPseudo(physicals, curr_pseudos)[axis - 1]

    def CalcAllPhysical(self, pseudos, curr_physicals):
        z, pit, rol = pseudos

        z = z / 1000.0  # change unit: mm -> m
        pit = pit / 1000.0  # change unit: mrad -> rad
        rol = rol / 1000.0  # change unit: mrad -> rad

        mzc_off = tan(pit) * self.dim_y / 2
        mzc = z + mzc_off
        mzl_off = tan(rol) * self.dim_x / 2
        mzl = z - mzc_off + mzl_off
        mzr = z - mzc_off - mzl_off

        mzc = mzc * 1000  # change unit: m -> mm
        mzl = mzl * 1000  # change unit: m -> mm
        mzr = mzr * 1000  # change unit: m -> mm

        return (mzc, mzl, mzr)

    def CalcAllPseudo(self, physicals, curr_pseudos):
        mzc, mzl, mzr = physicals

        mzc = mzc / 1000.0  # change unit: mm -> m
        mzl = mzl / 1000.0  # change unit: mm -> m
        mzr = mzr / 1000.0  # change unit: mm -> m

        pit = atan2((mzc - (mzr + mzl) / 2), self.dim_y)
        rol = atan2((mzl - mzr), self.dim_x)
        z = mzc / 2 + (mzl + mzr) / 4

        z = z * 1000  # change unit: mm -> m
        pit = pit * 1000  # change unit: rad -> mrad
        rol = rol * 1000  # change unit: rad -> mrad

        return (z, pit, rol)


class MirrorHorizontalPseudoMotorController(PseudoMotorController):
    """The PseudoMotor controller for mirror table horizontal pseudo motors.
    It provides x-translation and yaw angle based on physical translations:
    mx1 and mx2.

    The user units must be: mm for distances and mrad for angles.

    TYaw rotational axis is in the middle of Y dimension.

       ____________________________
      |                           |
      |                           |
      |                           |   <-------- beam direction
      |                           |
      |___________________________|
        ^ mx2                  ^ mx1

    For example of mirror with dim_y = 1262.5 increasing the yaw angle of
    1 mrad should increase the mx2 of 0.63125021041675084 mm and decrease
    the mx1 of 0.63125021041675084 mm.
    """

    pseudo_motor_roles = ('x', 'yaw')
    motor_roles = ('mx1', 'mx2')

    ctrl_properties = \
        {'dim_y': {Type : float,
                   Description : 'distance between mzc and mzr-mzl axis' }}

    def __init__(self, inst, props, *args, **kwargs):
        self.dim_y = self.dim_y / 1000.

    def CalcPhysical(self, axis, pseudos):
        # Don't do that!
        return self.CalcAllPhysical(pseudos)[axis - 1]

    def CalcPseudo(self, axis, physicals):
        # Don't do that!
        return self.CalcAllPseudo(physicals)[axis - 1]

    def CalcAllPhysical(self, pseudos):
        x, yaw = pseudos

        x_m = x / 1000.0
        yaw_rad = yaw / 1000.0

        mx1_m = x_m + tan(yaw_rad) * self.dim_y / 2
        mx2_m = x_m - tan(yaw_rad) * self.dim_y / 2

        mx1 = mx1_m * 1000
        mx2 = mx2_m * 1000

        return (mx1, mx2)

    def CalcAllPseudo(self, physicals):
        mx1, mx2 = physicals

        mx1_m = mx1 / 1000.0
        mx2_m = mx2 / 1000.0

        x_m = (mx1_m + mx2_m) / 2
        yaw_rad = atan2((mx1_m - mx2_m), self.dim_y)

        x = x_m * 1000
        yaw = yaw_rad * 1000

        return (x, yaw)
