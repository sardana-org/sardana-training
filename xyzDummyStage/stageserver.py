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
        self.clientsock = None

    def run(self):
        try:
            self.clientsock, addr = self.serversock.accept()
            while True:
                data = self.clientsock.recv(4096)
                if data == '': break
                ans = self.parse_cmd(data.lower().strip())
                self.clientsock.send(ans)
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

        ### TODO: MOVE MULTIPLE
        ###       ACCELERATION + VELOCITY + ?LIMITS?
        ###       IMPLEMENT MULTIPLE CLIENT CONNECTIONS? MAY HELP DEBUGGING :-D
        return ans+'\n'

    def shutdown(self):
        if self.clientsock is not None:
            self.clientsock.shutdown(0)
        self.serversock.shutdown(0)


def clear():
    global motors, x, y, z
    with lock:
        motors = [Motion(), Motion(), Motion()]
        x = [0]
        y = [0]
        z = [0]
        for m in motors:
            m.setMinVelocity(0)
            m.setMaxVelocity(100)
            m.setAccelerationTime(2)
            m.setDecelerationTime(2)
            m.setCurrentPosition(0)

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
    global motors, x, y, z
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


if __name__ == '__main__':
    global x, y, z, motors

    lock = Lock()
    clear()

    fig = plt.figure()
    fig.suptitle('Playing with an XYZ Dummy stage')
    ax = p3.Axes3D(fig)

    MAX_POINTS=1000
    xmax=1000
    point, = ax.plot([x[0]], [y[0]], [z[0]], 'o')
    line, = ax.plot(x, y, z, label='Trajectory')

    ax.legend()
    ax.set_xlim([-100, 100])
    ax.set_xlabel('X axis')
    ax.set_ylim([-100, 100])
    ax.set_ylabel('Y axis')
    ax.set_zlim([-100, 100])
    ax.set_zlabel('Z axis')


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


