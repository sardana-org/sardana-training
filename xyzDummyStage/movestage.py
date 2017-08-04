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
