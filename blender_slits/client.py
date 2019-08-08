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


import socket
import time


class Simu:

    def __init__(self, host='localhost', port=9999):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (host, port)
        self._sock.connect(server_address)

    def __del__(self):
        self._sock.close()

    def ask(self, cmd):
        self._sock.sendall(cmd+b'\n')
        ans = self._sock.recv(4096)
        print(cmd, b'->', ans[:-1])
        return ans

    def waitmove(self):
        ans = self.ask(b'?states')
        while b'MOVING' in ans:
            time.sleep(.5)
            ans = self.ask(b'?states')


if __name__ == '__main__':
    print("This scripts documents the hardware motor controller commands")
    s = Simu()
    print('\n\n# QUERY POSITION WITH ?pos <MOTOR>')
    s.ask(b'?pos top')
    s.ask(b'?pos bot')
    s.ask(b'?pos left')
    s.ask(b'?pos right')

    print('\n\n# QUERY POSITIONS WITH ?positions')
    s.ask(b'?positions')

    print('\n\n# QUERY STATE WITH ?state <MOTOR>')
    s.ask(b'?state top')
    s.ask(b'?state bot')
    s.ask(b'?state left')
    s.ask(b'?state right')

    print('\n\n# QUERY STATES WITH ?states')
    s.ask(b'?states')

    print('\n\n# MOVE BLADES BY ISSUING <MOTOR> <POS>')
    s.ask(b'top 50')
    s.ask(b'bot -50')
    s.ask(b'left -50')
    s.ask(b'right 50')
    s.waitmove()
    s.ask(b'?acq_im_file')
    s.ask(b'acq')
    s.ask(b'?acq_im_file')

    print('\n\n# MOVE MULTIPLE BY ISSUING move <MOTOR1> <POS1> <MOTOR2> <POS2> ...')
    s.ask(b'move right 20 top 20 bot -20 left -20')
    s.waitmove()

    print('\n\n# CHANGE VELOCITY WITH: vel <MOTOR> <VALUE>')
    s.ask(b'vel top 1000')
    s.ask(b'vel bot 500')
    s.ask(b'vel left 50')
    s.ask(b'vel right 10')

    print('\n\n# CHANGE ACCELERATION TIME WITH: acc <MOTOR> <VALUE>')
    s.ask(b'acc top 1')
    s.ask(b'acc bot 2')
    s.ask(b'acc left 3')
    s.ask(b'acc right 4')
    s.ask(b'move right 50 top 50 bot -50 left -50')
    s.waitmove()

    print('\n\n# ABORT _ANY_ MOTION WITH abort')
    s.ask(b'move right 20 top 20 bot -20 left -20')
    for i in range(10):
        time.sleep(.1)
    s.ask(b'abort')
    s.ask(b'?positions')
    s.ask(b'move right 20 top 20 bot -20 left -20')
    s.waitmove()
    s.ask(b'?positions')
    s.ask(b'?states')

    print('\n\n# CLOSE CONNECTION WITH q')
    s.ask(b'q')
