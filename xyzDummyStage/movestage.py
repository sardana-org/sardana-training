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

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 5000)
sock.connect(server_address)

def ask(cmd):
    sock.sendall(cmd+'\n')
    ans = sock.recv(4096)
    print cmd,'->',ans

ask('color blue')
ask('states')
ask('positions')
ask('move x 100')
ask('move y 100')
ask('move z 100')
ask('label z Z')
ask('states')
time.sleep(2)
ask('clear')
ask('color orange')
ask('positions')
ask('abort')
ask('states')
