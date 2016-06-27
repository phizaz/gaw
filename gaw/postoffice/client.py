from __future__ import print_function, absolute_import
from eventlet.green import socket
from gaw.postoffice.core import send, recieve

class PostofficeClient:

    def __init__(self, ip, port, verbose=False):
        self.ip = ip
        self.port = port
        self.verbose = verbose

        self.socket = socket.socket()
        self.socket.connect((ip, port))

    def send(self, data):
        if self.verbose:
            print('postofficeclient: sending data', data)

        send(self.socket, data)

        if self.verbose:
            print('postofficeclient: sending done')

        response = recieve(self.socket)

        if self.verbose:
            print('postofficeclient: receciving done')

        return response