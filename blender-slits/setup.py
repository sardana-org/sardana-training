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

"""The setup script."""

import sys
from setuptools import setup, find_packages


if sys.version_info < (3, 5):
    print('sls needs python >= 3.5')
    exit(1)

requirements = ['numpy', 'gevent', 'h5py', 'pillow']

setup_requirements = []

setup(
    name='blender_slits',
    author="ALBA Synchrotron",
    author_email='coutinhotiago@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    description="Blender slits server",
    entry_points={
        'console_scripts': [
            'blender-slits-server=blender_slits.main:run',
        ]
    },
    install_requires=requirements,
    license="MIT license",
    long_description="Blender slits server",
    include_package_data=True,
    keywords='blender, simulator, slit',
    packages=find_packages(include=['blender_slits']),
    package_data={
        'blender_slits': ['slits.blend']
    },
    setup_requires=setup_requirements,
    url='https://github.com/sardana-org/blender-slits',
    version='0.1.0'
)
