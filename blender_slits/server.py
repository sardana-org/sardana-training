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
import itertools
import numpy as np
import h5py
from PIL import Image

from threading import Thread
from Motion import Motion

scene = bge.logic.getCurrentScene()
top = scene.objects['b_top']
bot = scene.objects['b_bot']
left = scene.objects['b_left']
right = scene.objects['b_right']
cam = scene.objects['Camera']


class Acquisition:

    def __init__(self, detector, exposure_time, nb_frames,
                 saving_directory, image_format):
        self.detector = detector
        self.exposure_time = exposure_time
        self.nb_frames = nb_frames
        self.saving_directory = saving_directory
        self.image_format = image_format
        self.status = 'Ready'
        self.start_time = None
        self.end_time = None
        self.task = None
        self.stopped = False
        self.images = []

    def prepare(self):
        if self.saving_directory:
            os.makedirs(self.saving_directory, exist_ok=True)

    def acquire(self):
        self.detector.log.info(
            'start acquisition nb_frames=%s exposure_time=%ss',
            self.nb_frames, self.exposure_time)
        try:
            self._acquire()
        finally:
            self.status = 'Ready'
        self.detector.log.info('Finished acquisition')

    def _acquire(self):
        self.start_time = time.time()
        for frame in range(self.nb_frames):
            if self.stopped:
                break
            self.status = 'Acquiring #{}'.format(frame)
            det_render = self.detector.render()
            end = time.time()
            nap = self.exposure_time - (end - self.start_time)
            if nap > 0:
                time.sleep(nap)
            self.status = 'Readout #{}'.format(frame)
            # 512x256
            width, height = det_render.size
            image = det_render.image
            a = np.asarray(image, dtype=np.uint8)
            rgba_array = a.reshape((height, width, 4))
            gray_array = rgb2gray(rgba_array)
            im = Image.frombytes('RGBA', (width, height), rgba_array.tobytes())
            if self.saving_directory and self.image_format:
                self.status = 'Saving #{}'.format(frame)
                image_nb = self.detector.next_image_number()
                image_name = self.image_format.format(image_nb=image_nb)
                image_path = pathlib.Path(self.saving_directory, image_name)
                h5f = h5py.File(image_path.with_suffix('.h5'), "w")
                h5f.create_dataset("img", data=gray_array.astype(np.uint8))
                im.save(image_path.with_suffix('.png'))
                self.detector.last_image_file_name = image_path.with_suffix('.h5')
        self.end_time = time.time()
        self.status = 'Ready'

    def start(self):
        if self.task is not None:
            raise RuntimeError('Cannot start same acquisition twice')
        self.task = Thread(target=self.acquire)
        self.task.start()

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
        self.image_format = 'image-{image_nb:03d}'
        self.last_image_file_name = ''
        self.saving_directory = ''
        self.log = logging.getLogger(name)

    def render(self):
        return bge.texture.ImageRender(self.scene, self.obj)

    def next_image_number(self):
        return next(self.image_counter)

    @property
    def obj(self):
        return self.scene.objects[self.name]

    @property
    def acq_status(self):
        return 'Ready' if self.acq is None else self.acq.status

    def prepare_acquisition(self):
        self.acq = Acquisition(self, self.exposure_time, self.nb_frames,
                               self.saving_directory, self.image_format)
        self.acq.prepare()

    def start_acquisition(self):
        if self.acq_status != 'Ready':
            raise RuntimeError('Previous acquisition not finished yet!')
        self.acq.start()

    def stop_acquisition(self, wait=False):
        acq = self.acq
        if acq:
            acq.stopped = True
            if wait:
                self.acq.wait()

detector = Detector(scene, 'Detector')

# WELL-ALIGNED (GAP 0) POSITIONS ARE:
# top z=2   (4x2x1)+ROTX90
# bot z=-2  (4x2x1)+ROTX90
# left x=-2 (2x4x1)+ROTX90
# right x=2 (2x4x1)+ROTX90

m_top = Motion()
m_bot = Motion()
m_left = Motion()
m_right = Motion()
motor_names = [b'top', b'bot', b'left', b'right']
motors = {b'top': m_top,
          b'bot': m_bot,
          b'left': m_left,
          b'right': m_right}

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


def rgb2gray(rgb):
    return np.dot(rgb[..., :3], [0.2989, 0.5870, 0.1140])


def handle_sock(clientsock, addr):
    global PLAYING
    while PLAYING:
        try:
            bge.logic.NextFrame()
            data = clientsock.recv(4096)
            cmd = data.lower().strip()
            if not data: break
            if cmd == b'q':
                clientsock.close()
                return
            try:
                ans = execute_cmd(cmd)
                if ans is None:
                    ans = 'Ready\n'
                clientsock.sendall(ans.encode('utf-8'))
                debugline = 'cmd: '
                debugline += cmd.decode('utf-8')
                debugline += '  ->  '
                debugline += ans[:-1]
                print(debugline)
            except Exception as e:
                print(str(e))
        except:
            pass


def prepare_acq():
    try:
        detector.prepare_acquisition()
        return 'OK\n'
    except Exception as err:
        return 'ERROR: {}\n'.format(err)


def start_acq():
    try:
        detector.start_acquisition()
        return 'OK\n'
    except Exception as err:
        return 'ERROR: {}\n'.format(err)


def execute_cmd(cmd):
    global PLAYING, motors
    cmd_args = cmd.split()
    if cmd_args[0] in motor_names:
        # <motor> <value>
        m = motors[cmd_args[0]]
        cmd_v = float(cmd_args[1])
        p = m.getCurrentPosition()
        m.startMotion(p, cmd_v)

    if cmd.startswith(b'abort'):
        for m in motors.values():
            m.abortMotion()

    if cmd.startswith(b'move'):
        pairs = cmd_args[1:]
        for n, v in zip(pairs[::2], pairs[1::2]):
            m = motors[n]
            cmd_v = float(v)
            p = m.getCurrentPosition()
            m.startMotion(p, cmd_v)

    if cmd_args[0] in [b'acc', b'vel']:
        # <acc/vel> <motor> <value>
        cmd_m = motors[cmd_args[1]]
        cmd_v = float(cmd_args[2])

    if cmd.startswith(b'vel'):
        cmd_m.setMaxVelocity(cmd_v)

    if cmd.startswith(b'acc'):
        cmd_m.setAccelerationTime(cmd_v)
        cmd_m.setDecelerationTime(cmd_v)

    if cmd_args[0] in [b'?pos', b'?state', b'?vel', b'?acc']:
        cmd_m = motors[cmd_args[1]]
        ans = cmd_args[0][1:].decode('utf-8')
        ans += ' ' + cmd_args[1].decode('utf-8')
        if cmd_args[0] == b'?pos':
            ans += ' ' + str(cmd_m.getCurrentPosition())
            print(ans)
        if cmd_args[0] == b'?state':
            if cmd_m.isInMotion():
                ans += ' MOVING'
            else:
                ans += ' ON'
        if cmd_args[0] == b'?acc':
            ans += ' ' + str(cmd_m.getAccelerationTime())
        if cmd_args[0] == b'?vel':
            ans += ' ' + str(cmd_m.getMaxVelocity())
        return ans + '\n'

    if cmd.startswith(b'?positions'):
        l = []
        for n in motor_names:
            l.append(str(motors[n].getCurrentPosition()))
        ans = ' '.join(l)
        return ans + '\n'

    if cmd.startswith(b'?states'):
        states = []
        for n in motor_names:
            if motors[n].isInMotion():
                states.append('MOVING')
            else:
                states.append('ON')
        ans = ' '.join(states)
        return ans + '\n'

    if cmd.startswith(b'?acq_exposure_time'):
        return 'acq_exposure_time {}\n'.format(detector.exposure_time)

    if cmd.startswith(b'?acq_nb_frames'):
        return 'acq_nb_frames {}\n'.format(detector.nb_frames)

    if cmd.startswith(b'?acq_saving_directory'):
        return 'acq_saving_directory {}\n'.format(detector.saving_directory)

    if cmd.startswith(b'?acq_image_format'):
        return 'acq_image_format {}\n'.format(detector.image_format)

    if cmd.startswith(b'?acq_status'):
        return 'acq_status {}\n'.format(detector.acq_status)

    if cmd.startswith(b'?acq_last_image_file_name'):
        return 'acq_last_image_file_name {}\n'.format(detector.last_image_file_name)

    if cmd.startswith(b'acq_exposure_time'):
        detector.exposure_time = float(cmd.split()[1])

    if cmd.startswith(b'acq_nb_frames'):
        detector.nb_frames = int(cmd.split()[1])

    if cmd.startswith(b'acq_saving_directory'):
        detector.saving_directory = cmd.split()[1].decode()

    if cmd.startswith(b'acq_image_format'):
        detector.image_format = cmd.split()[1].decode()

    if cmd.startswith(b'acq_prepare'):
        return prepare_acq()

    if cmd.startswith(b'acq_start'):
        return start_acq()


def handle_keyboard():
    global PLAYING
    keyboard = bge.logic.keyboard
    while PLAYING:
        try:
            bge.logic.NextFrame()
            if keyboard.events[bge.events.LEFTARROWKEY] != 0:
                cam.applyMovement([-0.1, 0, 0], True)
            elif keyboard.events[bge.events.RIGHTARROWKEY] != 0:
                cam.applyMovement([0.1, 0, 0], True)
            elif keyboard.events[bge.events.UPARROWKEY] != 0:
                cam.applyMovement([0, 0.1, 0], True)
            elif keyboard.events[bge.events.DOWNARROWKEY] != 0:
                cam.applyMovement([0, -0.1, 0], True)
            time.sleep(.01)
        except:
            pass


def handle_mouse():
    global PLAYING
    mouse = bge.logic.mouse
    while PLAYING:
        try:
            bge.logic.NextFrame()
            if mouse.events[bge.events.WHEELUPMOUSE] != 0:
                cam.lens += 5
            elif mouse.events[bge.events.WHEELDOWNMOUSE] != 0:
                cam.lens -= 5
            elif mouse.events[bge.events.LEFTMOUSE] != 0:
                cam.applyRotation([0, 0.01, 0], True)
            elif mouse.events[bge.events.RIGHTMOUSE] != 0:
                cam.applyRotation([0, -0.01, 0], True)
            time.sleep(.01)
        except:
            pass


def update_positions():
    global PLAYING, m_top, m_bot, m_left, m_right
    while PLAYING:
        try:
            bge.logic.NextFrame()
            top.localPosition[2] = m_top.getCurrentPosition() / 10.0
            bot.localPosition[2] = m_bot.getCurrentPosition() / 10.0
            left.localPosition[0] = m_left.getCurrentPosition() / 10.0
            right.localPosition[0] = m_right.getCurrentPosition() / 10.0
        except:
            pass

        # CONFIGURE TCP SERVER


logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(levelname)-5s %(name)s: %(message)s')
PLAYING = True
serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversock.bind(('127.0.0.1', 9999))
serversock.listen(1)

tk = Thread(target=handle_keyboard, args=())
tk.daemon = True
tk.start()
tm = Thread(target=handle_mouse, args=())
tm.daemon = True
tm.start()
tup = Thread(target=update_positions, args=())
tup.daemon = True
tup.start()

print("Exit with Ctrl+C.")
try:
    while PLAYING:
        bge.logic.NextFrame()
        print("Waiting for connection...")
        clientsock, addr = serversock.accept()
        print('...connected from:', addr)
        ts = Thread(target=handle_sock, args=(clientsock, addr))
        ts.daemon = True
        ts.start()
except KeyboardInterrupt:
    PLAYING = False
    print('Ctrl-C pressed. Bailing out!')
finally:
    serversock.shutdown(socket.SHUT_RDWR)
    serversock.close()

tk.join()
tm.join()
tup.join()
