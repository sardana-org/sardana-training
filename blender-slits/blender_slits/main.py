# -*- coding: utf-8 -*-
# This file is part of Sardana-Training documentation
# 2019 ALBA Synchrotron
#
# Sardana-Training documentation is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sardana-Training documentation is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Sardana-Training.  If not, see <http://www.gnu.org/licenses/>.

import subprocess
import pkg_resources

def run():
    blender_filename = pkg_resources.resource_filename('blender_slits',
                                                       'slits.blend')
    try:
        subprocess.call(['blenderplayer', blender_filename])
    except KeyboardInterrupt:
        print('Ctrl-C pressed. Bailing out')
