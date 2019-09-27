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

import bge
import os
import time
import socket
import logging
import pathlib
import functools
import itertools
import numpy as np
import h5py
from PIL import Image

import gevent.server
from motion import Motion

log = logging.getLogger('server')


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
        data = np.asarray(canvas.image, dtype=np.uint8)
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
                start = time.time()
                h5f = h5py.File(image_path.with_suffix('.h5'), "w")
                h5f.create_dataset("img", data=gray_array.astype(np.uint8))
                log.info('HDF5 save time: %fs', time.time() - start)
                detector.last_image_file_name = image_path
            elif image_path.suffix == '.png':
                start = time.time()
                im = Image.fromarray(rgba_array, 'RGBA')
                im.save(image_path.with_suffix('.png'))
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


def rgb2gray(rgb):
    return np.dot(rgb[..., :3], [0.2989, 0.5870, 0.1140])


def handle_sock(sock, addr, cmd_handler):
    log.info('client at %r connected', addr)

    while True:
        try:
            data = sock.recv(4096)
            cmd = data.lower().strip().decode()
            if not data:
                log.info('client at %r disconnected', addr)
                return
            if cmd == 'q':
                log.info('client at %r quit', addr)
                sock.close()
                return
            try:
                ans = cmd_handler(cmd=cmd)
                if ans is None:
                    ans = 'Ready\n'
                if not isinstance(ans, bytes):
                    ans = ans.encode()
                sock.sendall(ans)
                log_ans = ans if len(ans) < 80 else ans[:75] + b'[...]'
                log.info('cmd: %r -> %r', cmd, log_ans)
            except Exception as err:
                sock.sendall('ERROR: {!r}\n'.format(err).encode())
                log.exception('Error running %r', cmd)
        except:
            pass


def execute_motor_cmd(cmd, config):
    motors = config['motors']
    motor_names = tuple(motors)
    cmd_args = cmd.split()
    if cmd_args[0] in motor_names:
        # <motor> <value>
        m = motors[cmd_args[0]]
        cmd_v = float(cmd_args[1])
        p = m.getCurrentPosition()
        m.startMotion(p, cmd_v)

    if cmd.startswith('abort'):
        for m in motors.values():
            m.abortMotion()

    if cmd.startswith('move'):
        pairs = cmd_args[1:]
        for n, v in zip(pairs[::2], pairs[1::2]):
            m = motors[n]
            cmd_v = float(v)
            p = m.getCurrentPosition()
            m.startMotion(p, cmd_v)

    if cmd_args[0] in ['acc', 'vel']:
        # <acc/vel> <motor> <value>
        cmd_m = motors[cmd_args[1]]
        cmd_v = float(cmd_args[2])

    if cmd.startswith('vel'):
        cmd_m.setMaxVelocity(cmd_v)

    if cmd.startswith('acc'):
        cmd_m.setAccelerationTime(cmd_v)
        cmd_m.setDecelerationTime(cmd_v)

    if cmd_args[0] in ['?pos', '?state', '?vel', '?acc']:
        cmd_m = motors[cmd_args[1]]
        ans = cmd_args[0][1:]
        ans += ' ' + cmd_args[1]
        if cmd_args[0] == '?pos':
            ans += ' ' + str(cmd_m.getCurrentPosition())
        if cmd_args[0] == '?state':
            if cmd_m.isInMotion():
                ans += ' MOVING'
            else:
                ans += ' ON'
        if cmd_args[0] == '?acc':
            ans += ' ' + str(cmd_m.getAccelerationTime())
        if cmd_args[0] == '?vel':
            ans += ' ' + str(cmd_m.getMaxVelocity())
        return ans + '\n'

    if cmd.startswith('?positions'):
        l = []
        for n in motor_names:
            l.append(str(motors[n].getCurrentPosition()))
        ans = ' '.join(l)
        return ans + '\n'

    if cmd.startswith('?states'):
        states = []
        for n in motor_names:
            if motors[n].isInMotion():
                states.append('MOVING')
            else:
                states.append('ON')
        ans = ' '.join(states)
        return ans + '\n'

    if cmd == 'error':
        raise Exception('Hey! You did that on purpose!')

    return 'ERROR: Unknown command {!r}\n'.format(cmd)


def execute_detector_cmd(cmd, config):
    detector = config['detector']
    if cmd == '?acq_image':
        data = detector.last_image_acquired
        import pickle
        data = pickle.dumps(data)
        size = len(data)
        return '{:08d}'.format(size).encode() + data

    elif cmd == '?acq_exposure_time':
        return 'acq_exposure_time {}\n'.format(detector.exposure_time)

    elif cmd == '?acq_nb_frames':
        return 'acq_nb_frames {}\n'.format(detector.nb_frames)

    elif cmd == '?acq_saving_directory':
        return 'acq_saving_directory {}\n'.format(detector.saving_directory)

    elif cmd == '?acq_image_name':
        return 'acq_image_name {}\n'.format(detector.image_name)

    elif cmd == '?acq_status':
        return 'acq_status {}\n'.format(detector.acq_status)

    elif cmd == '?acq_last_image_file_name':
        return 'acq_last_image_file_name {}\n'.format(detector.last_image_file_name)

    elif cmd.startswith('acq_exposure_time'):
        detector.exposure_time = float(cmd.split()[1])
        return 'OK\n'

    elif cmd.startswith('acq_nb_frames'):
        detector.nb_frames = int(cmd.split()[1])
        return 'OK\n'

    elif cmd.startswith('acq_saving_directory'):
        detector.saving_directory = cmd.split()[1]
        return 'OK\n'

    elif cmd.startswith('acq_image_name'):
        detector.image_name = cmd.split()[1]
        return 'OK\n'

    elif cmd.startswith('acq_prepare'):
        detector.prepare_acquisition()
        return 'OK\n'

    elif cmd.startswith('acq_start'):
        detector.start_acquisition()
        return 'OK\n'

    elif cmd.startswith('acq_stop'):
        detector.stop_acquisition()
        return 'OK\n'

    if cmd == 'error':
        raise Exception('Hey! You did that on purpose!')

    return 'ERROR: Unknown command {!r}\n'.format(cmd)


def update_frame(config):
    top, bot, left, right = config['top'], config['bot'], config['left'], config['right']
    motions = any(map(Motion.isInMotion, (top, bot, left, right)))
    if motions:
        top.blender.localPosition[2] = top.getCurrentPosition() / 10.0
        bot.blender.localPosition[2] = bot.getCurrentPosition() / 10.0
        left.blender.localPosition[0] = left.getCurrentPosition() / 10.0
        right.blender.localPosition[0] = right.getCurrentPosition() / 10.0
        bge.logic.NextFrame()


def run():
    fmt = '%(asctime)-15s %(levelname)-5s %(threadName)s %(name)s: %(message)s'
    logging.basicConfig(level=logging.INFO, format=fmt)

    scene = bge.logic.getCurrentScene()
    top = scene.objects['b_top']
    bot = scene.objects['b_bot']
    left = scene.objects['b_left']
    right = scene.objects['b_right']

    detector = Detector(scene, 'Detector')

    # WELL-ALIGNED (GAP 0) POSITIONS ARE:
    # top z=2   (4x2x1)+ROTX90
    # bot z=-2  (4x2x1)+ROTX90
    # left x=-2 (2x4x1)+ROTX90
    # right x=2 (2x4x1)+ROTX90

    m_top = Motion()
    m_top.blender = top
    m_bot = Motion()
    m_bot.blender = bot
    m_left = Motion()
    m_left.blender = left
    m_right = Motion()
    m_right.blender = right
    motors = {'top': m_top,
              'bot': m_bot,
              'left': m_left,
              'right': m_right}

    config = dict(motors, motors=motors, detector=detector)

    for m in motors.values():
        m.setMinVelocity(0)
        m.setMaxVelocity(100)
        m.setAccelerationTime(0.1)
        m.setDecelerationTime(0.1)
        m.setCurrentPosition(0)

    # MOVE TO START POSITION
    m_top.startMotion(0, 20)
    m_bot.startMotion(0, -50)
    m_left.startMotion(0, -50)
    m_right.startMotion(0, 20)

    motor_cmd_func = functools.partial(execute_motor_cmd, config=config)
    def handle_motor_ctrl(sock, addr):
        handle_sock(sock, addr, motor_cmd_func)
    motor_ctrl_server = gevent.server.StreamServer(('0', 9999),
                                                   handle_motor_ctrl)

    det_cmd_func = functools.partial(execute_detector_cmd, config=config)
    def handle_det_ctrl(sock, addr):
        handle_sock(sock, addr, det_cmd_func)
    det_ctrl_server = gevent.server.StreamServer(('0', 9998),
                                                 handle_det_ctrl)

    motor_ctrl_server.start()
    det_ctrl_server.start()
    log.info("Ready to accept requests!")
    log.info("Exit with Ctrl-C.")

    try:
        while True:
            update_frame(config)
            gevent.sleep(1/30)
    except KeyboardInterrupt:
        log.info('Ctrl-C pressed. Bailing out!')
    motor_ctrl_server.stop()
    det_ctrl_server.stop()
    return 0
