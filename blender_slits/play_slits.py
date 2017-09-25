import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 9999)
sock.connect(server_address)

def ask(cmd):
    sock.sendall(cmd+'\n')
    ans = sock.recv(4096)
    print cmd,'->',ans[:-1]
    return ans

print("This scripts documents the hardware motor controller commands")

def waitmove():
    ans = ask('?states')
    while 'MOVING' in ans:
        time.sleep(.5)
        ans = ask('?states')

print('\n\n# QUERY POSITION WITH ?pos <MOTOR>')
ask('?pos top')
ask('?pos bot')
ask('?pos left')
ask('?pos right')

print('\n\n# QUERY POSITIONS WITH ?positions')
ask('?positions')

print('\n\n# QUERY STATE WITH ?state <MOTOR>')
ask('?state top')
ask('?state bot')
ask('?state left')
ask('?state right')

print('\n\n# QUERY STATES WITH ?states')
ask('?positions')

print('\n\n# MOVE BLADES BY ISSUING <MOTOR> <POS>')
ask('top 50')
ask('bot -50')
ask('left -50')
ask('right 50')
waitmove()

print('\n\n# MOVE MULTIPLE BY ISSUING move <MOTOR1> <POS1> <MOTOR2> <POS2> ...')
ask('move right 20 top 20 bot -20 left -20')
waitmove()

print('\n\n# CHANGE VELOCITY WITH: vel <MOTOR> <VALUE>')
ask('vel top 1000')
ask('vel bot 500')
ask('vel left 50')
ask('vel right 10')

print('\n\n# CHANGE ACCELERATION TIME WITH: acc <MOTOR> <VALUE>')
ask('acc top 1')
ask('acc bot 2')
ask('acc left 3')
ask('acc right 4')
ask('move right 50 top 50 bot -50 left -50')
waitmove()

print('\n\n# ABORT _ANY_ MOTION WITH abort')
ask('move right 20 top 20 bot -20 left -20')
for i in range(10):
    time.sleep(.1)
ask('abort')
ask('?positions')
ask('move right 20 top 20 bot -20 left -20')
waitmove()
ask('?positions')
ask('?states')

print('\n\n# CLOSE CONNECTION WITH q')
ask('q')
