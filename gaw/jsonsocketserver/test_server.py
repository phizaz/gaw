from __future__ import print_function
from gaw.jsonsocketserver.server import JsonSocketServer

def home(path):
    print('home!')
    print('path:', path)
    raise ValueError('test error')

def plus(a, b, path):
    print('plus!')
    print('path:', path)
    return a + b

server = JsonSocketServer('0.0.0.0', 4444, secret='Qx9XFxN17+zkUdcBIGZ0A1sQTkUSP4SZ', is_encrypt=True)
server.register_route('home', home)
server.register_route('plus', plus)
server.start()