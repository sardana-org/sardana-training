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


import random
import socket
from threading import Lock
from threading import Thread

import matplotlib.pyplot as plt
import matplotlib.animation as anim
import mpl_toolkits.mplot3d.axes3d as p3

from sardana.pool.poolcontrollers.DummyMotorController import Motion

class SocketListenerThread(Thread):
    def __init__(self, serversock):
        Thread.__init__(self)
        self.serversock = serversock
        self.serve = True
        self.clientsock = None

    def run(self):
        while self.serve:
            try:
                self.clientsock, addr = self.serversock.accept()
                try:
                    while True:
                        data = self.clientsock.recv(4096)
                        if data == '': break
                        ans = self.parse_cmd(data.lower().strip())
                        self.clientsock.send(ans)
                except Exception,e:
                    pass # forced by a socket shutdown
            except Exception,e:
                pass # forced by a socket shutdown

    def parse_cmd(self, cmd):
        ans = 'NOK:'+cmd
        if cmd == 'clear':                          # CLEAR: will erase the plot
            clear()
            ans = 'OK:'+cmd+':cleared'
        if cmd == 'states':                         # STATES: '<ON|MOVING> <ON|MOVING> <ON|MOVING>' 
            ans = 'OK:'+cmd+':'+get_states()
        if cmd == 'positions':                      # POSITIONS: '<POS> <POS> <POS>' 
            ans = 'OK:'+cmd+':'+get_positions()
        if cmd == 'abort':                          # ABORT: stop all motions
            abort()
            ans = 'OK:'+cmd+':aborted'
        if cmd.startswith('move'):                  # MOVE <X|Y|Z> <POS>' 
            ans = 'OK:'+cmd+':'+move_motor(cmd)
        if cmd.startswith('label'):
            _, axis, label = cmd.split(' ', 2) 
            set_label(axis, label)
            ans = 'OK:'+cmd+':'+label
        if cmd.startswith('color'):
            _, color = cmd.split()
            set_color(color)
            ans = 'OK:'+cmd+':'+color
        'label x text'
        ### TODO: MOVE MULTIPLE
        ###       ACCELERATION + VELOCITY + ?LIMITS?
        ###       IMPLEMENT MULTIPLE CLIENT CONNECTIONS? MAY HELP DEBUGGING :-D
        return ans+'\n'

    def shutdown(self):
        if self.clientsock is not None:
            self.clientsock.shutdown(0)
        self.serve = False
        self.serversock.shutdown(0)


def clear():
    global motors, x, y, z, color, xlabel, ylabel, zlabel
    with lock:
        motors = [Motion(), Motion(), Motion()]
        x = [0]
        y = [0]
        z = [0]
        color = 'red' 
        xlabel = 'X axis'
        ylabel = 'Y axis'
        zlabel = 'Z axis'
        for m in motors:
            m.setMinVelocity(0)
            m.setMaxVelocity(100)
            m.setAccelerationTime(2)
            m.setDecelerationTime(2)
            m.setCurrentPosition(0)
        

def set_label(axis, label):
    global xlabel, ylabel, zlabel
    if axis.lower() == 'x':
        xlabel = label
    elif axis.lower() == 'y':
        ylabel = label
    elif axis.lower() == 'z':
        zlabel = label
#    return 'Axis {0} label has been changed'.format(axis)
     
            
def set_color(new_color):
    global color
    color = new_color
    
def set_legend_label(new_label):
    global label
    label = new_label

def get_states():
    global motors
    states = ['MOVING' if m.isInMotion() else 'ON' for m in motors]
    return ' '.join(states)
    
def get_positions():
    global motors
    positions = [str(m.getCurrentPosition()) for m in motors]
    return ' '.join(positions)
    
def move_motor(cmd):
    global motors
    try:
        _, axis, target_pos = cmd.split()
        target_pos = float(target_pos)
    except Exception,e:
        return 'EXCEPTION:'+str(e)
    axes = ['x','y','z']
    if axis not in axes:
        return 'ERROR: MOTOR_NAME should be X, Y, or Z'
    i = axes.index(axis)
    m = motors[i]
    if m.isInMotion():
        return 'ERROR: MOTOR is MOVING'
    m_pos = m.getCurrentPosition()
    m.startMotion(m_pos, target_pos)
    return axis+':('+str(m_pos)+'->'+str(target_pos)+')'

def abort():
    for m in motors:
        m.abortMotion()

def update(i):
    global motors, x, y, z, color
    with lock:
        if len(x) == MAX_POINTS:
            x.pop(0)
            y.pop(0)
            z.pop(0)
        x.append(motors[0].getCurrentUserPosition())
        y.append(motors[1].getCurrentUserPosition())
        z.append(motors[2].getCurrentUserPosition())
    point.set_data((x[-1], y[-1]))
    point.set_3d_properties(z[-1], 'z')
    line.set_data(x,y)
    line.set_3d_properties(z, 'z')
    # update color
    line.set_color(color)
    point.set_color(color)
    # update label
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)

if __name__ == '__main__':
    global x, y, z, motors, color, xlabel, ylabel, zlabel

    lock = Lock()
    clear()

    fig = plt.figure()
    fig.suptitle('Playing with an XYZ Dummy stage')
    ax = p3.Axes3D(fig)

    MAX_POINTS=1000
    xmax=1000
    
    color = 'red' 
    xlabel = 'X axis'
    ylabel = 'Y axis'
    zlabel = 'Z axis'
    
    point, = ax.plot([x[0]], [y[0]], [z[0]], 'o', color=color)
    line, = ax.plot(x, y, z, color=color)

    
    ax.set_xlim([-100, 100])
    ax.set_xlabel(xlabel)
    ax.set_ylim([-100, 100])
    ax.set_ylabel(ylabel)
    ax.set_zlim([-100, 100])
    ax.set_zlabel(zlabel)


    ADDR = ('127.0.0.1', 5000)
    serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversock.bind(ADDR)
    serversock.listen(1)
    slt = SocketListenerThread(serversock)
    slt.start()
    
    a = anim.FuncAnimation(fig, update, frames=xmax, repeat=True, interval=50)
    plt.show()
    slt.shutdown()


