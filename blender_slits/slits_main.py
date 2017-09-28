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
import time
import socket
from threading import Thread
import math
import mathutils
from Motion import Motion

#print('hello')
scene = bge.logic.getCurrentScene()
top = scene.objects['b_top']
bot = scene.objects['b_bot']
left = scene.objects['b_left']
right = scene.objects['b_right']
cam = scene.objects['Camera']
#print('objects ok')


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
    m.setMaxVelocity(10)
    m.setAccelerationTime(2)
    m.setDecelerationTime(2)
    m.setCurrentPosition(0)

# MOVE TO START POSITION
m_top.startMotion(0, 20)
m_bot.startMotion(0, -20)
m_left.startMotion(0, -20)
m_right.startMotion(0, 20)

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

def execute_cmd(cmd):
    global PLAYING, motors
    cmd_args = cmd.split()
    if cmd_args[0] in motor_names:
        #<motor> <value>
        m = motors[cmd_args[0]]
        cmd_v = float(cmd_args[1])
        p = m.getCurrentPosition()
        m.startMotion(p, cmd_v)

    if cmd.startswith(b'abort'):
        for m in motors.values():
            m.abortMotion()

    if cmd.startswith(b'move'):
        pairs = cmd_args[1:]
        for n,v in zip(pairs[::2], pairs[1::2]):
            m = motors[n]
            cmd_v = float(v)
            p = m.getCurrentPosition()
            m.startMotion(p, cmd_v)

    if cmd_args[0] in [b'acc', b'dec', b'vel']:
        #<acc/vel> <motor> <value>
        cmd_m = motors[cmd_args[1]]
        cmd_v = float(cmd_args[2])

    if cmd.startswith(b'vel'):
        cmd_m.setMaxVelocity(cmd_v)

    if cmd.startswith(b'acc'):
        cmd_m.setAccelerationTime(cmd_v)

    if cmd.startswith(b'dec'):
        cmd_m.setDecelerationTime(cmd_v)

    if cmd_args[0] in [b'?pos', b'?state', b'?vel', b'?acc', b'?dec']:
        cmd_m = motors[cmd_args[1]]
        ans = cmd_args[0][1:].decode('utf-8')
        ans += ' '+cmd_args[1].decode('utf-8')
        if cmd_args[0] == b'?pos':
            ans += ' '+str(cmd_m.getCurrentPosition())
            print(ans)
        if cmd_args[0] == b'?state':
            if cmd_m.isInMotion():
                ans += ' MOVING'
            else:
                ans += ' ON'
        if cmd_args[0] == b'?acc':
            ans += ' '+str(cmd_m.getAccelerationTime())
        if cmd_args[0] == b'?dec':
            ans += ' '+str(cmd_m.getDecelerationTime())
        if cmd_args[0] == b'?vel':
            ans += ' '+str(cmd_m.getMaxVelocity())
        return ans+'\n'        

    if cmd.startswith(b'?positions'):
        l = []
        for n in motor_names:
            l.append(str(motors[n].getCurrentPosition()))
        ans = ' '.join(l)
        return ans+'\n'

    if cmd.startswith(b'?states'):
        ans = cmd_args[0][1:].decode('utf-8')
        states = []
        for n in motor_names:
            if motors[n].isInMotion():
                states.append('MOVING')
            else:
                states.append('ON')
        ans += ' '.join(states)
        return ans+'\n'


def handle_keyboard():
    global PLAYING
    keyboard = bge.logic.keyboard
    while PLAYING:
        try:
            bge.logic.NextFrame()
            if keyboard.events[bge.events.LEFTARROWKEY] != 0:
                cam.applyMovement([-0.1,0,0], True)
            elif keyboard.events[bge.events.RIGHTARROWKEY] != 0:
                cam.applyMovement([0.1,0,0], True)
            elif keyboard.events[bge.events.UPARROWKEY] != 0:
                cam.applyMovement([0,0.1,0], True)
            elif keyboard.events[bge.events.DOWNARROWKEY] != 0:
                cam.applyMovement([0,-0.1,0], True)
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
                cam.applyRotation([0,0.01,0], True)
            elif mouse.events[bge.events.RIGHTMOUSE] != 0:
                cam.applyRotation([0,-0.01,0], True)        
            time.sleep(.01)
        except:
            pass

def update_positions():
    global PLAYING, m_top, m_bot, m_left, m_right
    while PLAYING:
        try:
            bge.logic.NextFrame()
            top.localPosition[2] = m_top.getCurrentPosition()/10.0
            bot.localPosition[2] = m_bot.getCurrentPosition()/10.0
            left.localPosition[0] = m_left.getCurrentPosition()/10.0
            right.localPosition[0] = m_right.getCurrentPosition()/10.0
        except:
            pass        
    
# CONFIGURE TCP SERVER
PLAYING = True
serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversock.bind(('127.0.0.1', 9999))
serversock.listen(1)

tk = Thread(target=handle_keyboard, args=())
tk.start()
tm = Thread(target=handle_mouse, args=())
tm.start()
tup = Thread(target=update_positions, args=())
tup.start()

print("Exit with Ctrl+C.")
while PLAYING:
    bge.logic.NextFrame()
    print("Waiting for connection...")
    clientsock, addr = serversock.accept()
    print('...connected from:', addr)
    ts = Thread(target=handle_sock, args=(clientsock, addr))
    ts.start()

serversock.shutdown(socket.SHUT_RDWR)
serversock.close()

#print('shutting down')