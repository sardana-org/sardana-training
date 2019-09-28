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

import os
import time
import logging
import pathlib
import itertools

import bge
import PIL
import h5py
import numpy
import gevent


def rgb2gray(rgb):
    return numpy.dot(rgb[..., :3], [0.2989, 0.5870, 0.1140])


class Acquisition:

    def __init__(self, detector, exposure_time, nb_frames,
                 saving_directory, image_name):
        self.detector = detector
        self.exposure_time = exposure_time
        self.saving_directory = saving_directory
        self.image_name = image_name
        self.status = 'Ready'
        self.start_time = None
        self.end_time = None
        self.task = None

    def prepare(self):
        if self.saving_directory:
            os.makedirs(self.saving_directory, exist_ok=True)

    def acquire(self):
        self.detector.log.info(
            'start acquisition exposure_time=%ss', self.exposure_time)
        try:
            self._acquire()
        finally:
            self.status = 'Ready'
        self.detector.log.info('Finished acquisition')

    def _acquire(self):
        detector = self.detector
        log = detector.log
        self.status = 'Acquiring'
        self.start_time = time.time()
        canvas = self.detector.render()
        data = numpy.asarray(canvas.image, dtype=numpy.uint8)
        width, height = canvas.size
        dt = self.exposure_time - (time.time() - self.start_time)
        if dt > 0:
            gevent.sleep(dt)
        self.status = 'Readout'
        # 512x256
        start = time.time()
        rgba_array = data.reshape((height, width, 4))
        gray_array = rgb2gray(rgba_array)
        detector.last_image_acquired = gray_array
        log.info('Readout time: %fs', time.time() - start)
        if self.saving_directory and self.image_name:
            self.status = 'Saving'
            image_nb = detector.next_image_number()
            image_name = self.image_name.format(image_nb=image_nb)
            image_path = pathlib.Path(self.saving_directory, image_name)
            if image_path.suffix == '.h5':
                log.info('Saving HDF5 to %r', image_path)
                start = time.time()
                h5f = h5py.File(image_path, "w")
                h5f.create_dataset("img", data=gray_array.astype(numpy.uint8))
                log.info('HDF5 save time: %fs', time.time() - start)
                detector.last_image_file_name = image_path
            elif image_path.suffix == '.png':
                start = time.time()
                im = PIL.Image.fromarray(rgba_array, 'RGBA')
                im.save(image_path)
                log.info('PNG save time: %fs', time.time() - start)
                detector.last_image_file_name = image_path
            else:
                log.warning('Unknown saving extension %r. File not saved', image_path.suffix)
        self.end_time = time.time()
        self.status = 'Ready'

    def start(self):
        if self.task is not None:
            raise RuntimeError('Cannot start same acquisition twice')
        self.task = gevent.spawn(self.acquire)

    def stop(self):
        if self.task is not None:
            self.task.kill()

    def wait(self):
        self.task.join()


class Detector:

    def __init__(self, scene, name):
        self.scene = scene
        self.name = name
        self.exposure_time = 1.0
        self.nb_frames = 1
        self.image_counter = itertools.count()
        self.acq = None
        self.image_name = 'image-{image_nb:03d}.h5'
        self.last_image_file_name = ''
        self.last_image_acquired = None
        self.saving_directory = ''
        self.log = logging.getLogger(name)

    def render(self):
        return bge.texture.ImageRender(self.scene, self.blender)

    def next_image_number(self):
        return next(self.image_counter)

    @property
    def blender(self):
        return self.scene.objects[self.name]

    @property
    def acq_status(self):
        return 'Ready' if self.acq is None else self.acq.status

    def prepare_acquisition(self):
        self.acq = Acquisition(self, self.exposure_time, self.nb_frames,
                               self.saving_directory, self.image_name)
        self.acq.prepare()

    def start_acquisition(self):
        acq = self.acq
        if acq is None:
            raise RuntimeError('Need to call prepare first!')
        if acq.status != 'Ready':
            raise RuntimeError('Previous acquisition not finished yet!')
        acq.start()

    def stop_acquisition(self):
        acq = self.acq
        if acq:
            acq.stop()
