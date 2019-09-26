import socket
import select

from sardana import State
from sardana.pool.controller import (TwoDController, Referable, Type,
    Description, DefaultValue)


class BlenderDetectorError(Exception):
    pass


class BlenderDetector:

    def __init__(self, host, port):
        self._socket = None
        self._socket = socket.create_connection((host, port))
        self._acquiring = False

    def __del__(self):
        self._socket.close()

    def ask(self, command):
        command = "{0}\n".format(command)
        try:
            self._socket.sendall(command.encode())
            return self._socket.recv(4096).decode().strip()
        except:
            raise CommunicationError("send/recv failed")

    def prepare_acquisition(self):
        r = self.ask('acq_prepare')
        if r.startswith('ERROR'):
            raise BlenderDetectorError(r.split(' ', 1)[1])

    def start_acquisition(self):
        r = self.ask('acq_start')
        if r.startswith('ERROR'):
            raise BlenderDetectorError(r.split(' ', 1)[1])

    def stop_acquisition(self):
        r = self.ask('start_acq')
        assert 'OK' in r

    @property
    def acq_status(self):
        r = self.ask('?acq_status')
        return r.partition(' ')[-1]

    @property
    def nb_frames(self):
        r = self.ask('?acq_nb_frames')
        return int(r.partition(' ')[-1])

    @nb_frames.setter
    def nb_frames(self, nb_frames):
        self.ask('acq_nb_frames {}'.format(nb_frames))

    @property
    def exposure_time(self):
        r = self.ask('?acq_exposure_time')
        return float(r.partition(' ')[-1])

    @exposure_time.setter
    def exposure_time(self, exposure_time):
        self.ask('acq_exposure_time {}'.format(exposure_time))

    @property
    def saving_directory(self):
        r = self.ask('?acq_saving_directory')
        return r.partition(' ')[-1]

    @saving_directory.setter
    def saving_directory(self, directory):
        self.ask('acq_saving_directory {}'.format(directory))

    @property
    def image_format(self):
        r = self.ask('?acq_image_format')
        return r.partition(' ')[-1]

    @image_format.setter
    def image_format(self, fmt):
        self.ask('acq_image_format {}'.format(fmt))

    @property
    def last_image_file_name(self):
        r = self.ask('?acq_last_image_file_name')
        return r.partition(' ')[-1]


class Blender2DController(TwoDController, Referable):

    ctrl_properties = \
        {"Host": {
            Type : str,
            Description : "Host where runs the blender detector server",
            DefaultValue : "localhost"
        },
        "Port": {
            Type : int,
            Description : "Port the blender detector listens on",
            DefaultValue : 9999},
        }

    def __init__(self, inst, props, *args, **kwargs):
        super().__init__(inst, props, *args, **kwargs)
        self.detector = BlenderDetector(self.Host, self.Port)

    def StateOne(self, axis):
        status = self.detector.acq_status
        state = State.On if status == 'Ready' else State.Moving
        return state, status

    def PrepareOne(self, axis, value, repetitions, latency, nb_starts):
        pass

    def LoadOne(self, axis, integ_time, repetitions, latency_time):
        self.detector.exposure_time = integ_time
        self.detector.nb_frames = repetitions
        self.detector.prepare_acquisition()

    def StartOne(self, axis, value):
        print('START ONE', axis, value)
        try:
            self.detector.start_acquisition()
        except Exception as err:
            print('Error in START ONE', err)
            raise

    def ReadOne(self, axis):
        pass

    def AbortOne(self, axis):
        self.detector.stop_acquisition()

    def RefOne(self, axis):
        name = self.detector.last_image_file_name
        return 'file://{}'.format(name) if name else ''

    def SetAxisPar(self, axis, parameter, value):
        if parameter == "value_ref_pattern":
            path, fpattern = value.rsplit('/', 1)
            path = path.replace('file://', '')
            self.detector.saving_directory = path
            self.detector.image_format = fpattern


