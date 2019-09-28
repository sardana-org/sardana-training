#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
